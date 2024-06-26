# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class MrpReport(models.Model):
    _name = 'mrp.report'
    _description = "Manufacturing Report"
    _rec_name = 'production_id'
    _auto = False
    _order = 'date_finished desc'

    id = fields.Integer("", readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    production_id = fields.Many2one('mrp.production', "Manufacturing Order", readonly=True)
    date_finished = fields.Datetime('End Date', readonly=True)
    product_id = fields.Many2one('product.product', "Product", readonly=True)
    total_cost = fields.Float(
        "Total Cost", readonly=True,
        help="Total cost of manufacturing order (component + operation costs)")
    component_cost = fields.Float(
        "Total Component Cost", readonly=True,
        help="Total cost of components for manufacturing order")
    operation_cost = fields.Float(
        "Total Operation Cost", readonly=True, groups="mrp.group_mrp_routings",
        help="Total cost of operations for manufacturing order")
    duration = fields.Float(
        "Total Duration of Operations", readonly=True, groups="mrp.group_mrp_routings",
        help="Total duration (minutes) of operations for manufacturing order")

    qty_produced = fields.Float(
        "Quantity Produced", readonly=True,
        help="Total quantity produced in product's UoM")

    # note that unit costs take include subtraction of byproduct cost share
    unit_cost = fields.Float(
        "Cost / Unit", readonly=True, group_operator="avg",
        help="Cost per unit produced (in product UoM) of manufacturing order")
    unit_component_cost = fields.Float(
        "Component Cost / Unit", readonly=True, group_operator="avg",
        help="Component cost per unit produced (in product UoM) of manufacturing order")
    unit_operation_cost = fields.Float(
        "Total Operation Cost / Unit", readonly=True, group_operator="avg",
        groups="mrp.group_mrp_routings",
        help="Operation cost per unit produced (in product UoM) of manufacturing order")
    unit_duration = fields.Float(
        "Duration of Operations / Unit", readonly=True, group_operator="avg",
        groups="mrp.group_mrp_routings",
        help="Operation duration (minutes) per unit produced of manufacturing order")

    byproduct_cost = fields.Float(
        "By-Products Total Cost", readonly=True,
        groups="mrp.group_mrp_byproducts")

    @property
    def _table_query(self):
        ''' Report needs to be dynamic to take into account multi-company selected + multi-currency rates '''
        return '%s %s %s %s' % (self._select(), self._from(), self._where(), self._group_by())

    def _select(self):
        select_str = """
            SELECT
                min(mo.id)             AS id,
                mo.id                  AS production_id,
                mo.company_id          AS company_id,
                mo.date_finished       AS date_finished,
                mo.product_id          AS product_id,
                prod_qty.product_qty   AS qty_produced,
                comp_cost.total * currency_table.rate                                                                                   AS component_cost,
                op_cost.total * currency_table.rate                                                                                     AS operation_cost,
                (comp_cost.total + op_cost.total) * currency_table.rate                                                                 AS total_cost,
                op_cost.total_duration                                                                                                  AS duration,
                comp_cost.total * (1 - cost_share.byproduct_cost_share) / prod_qty.product_qty * currency_table.rate                    AS unit_component_cost,
                op_cost.total * (1 - cost_share.byproduct_cost_share) / prod_qty.product_qty * currency_table.rate                      AS unit_operation_cost,
                (comp_cost.total + op_cost.total) * (1 - cost_share.byproduct_cost_share) / prod_qty.product_qty * currency_table.rate  AS unit_cost,
                op_cost.total_duration / prod_qty.product_qty                                                                           AS unit_duration,
                (comp_cost.total + op_cost.total) * cost_share.byproduct_cost_share * currency_table.rate                               AS byproduct_cost
        """

        return select_str

    def _from(self):
        """ MO costs are quite complicated so the table is built with the following subqueries (per MO):
            1. total component cost (note we cover no components use case)
            2. total operations cost (note we cover no operations use case)
            3. total byproducts cost share
            4. total qty produced based on the product's UoM
        Note subqueries 3 and 4 exist because 3 subqueries use the stock_move table and combining them would result in duplicated SVL values and
        subquery 2 (i.e. the nested subquery) exists to prevent duplication of operation costs (i.e. 2+ comp lines and 2+ operations at diff wc in
        the same MO results in op cost duplication if op cost isn't aggregated first).
        Subqueries will return 0.0 as value whenever value IS NULL to prevent SELECT calculations from being nulled (e.g. there is no cost then
        it is mathematically 0 anyways).
        """
        from_str = """
            FROM mrp_production AS mo
            LEFT JOIN (
                SELECT
                    mo.id                                                                    AS mo_id,
                    CASE WHEN SUM(svl.value) IS NULL THEN 0.0 ELSE abs(SUM(svl.value)) END   AS total
                FROM mrp_production AS mo
                LEFT JOIN stock_move AS sm on sm.raw_material_production_id = mo.id
                LEFT JOIN stock_valuation_layer AS svl ON svl.stock_move_id = sm.id
                WHERE mo.state = 'done'
                    AND (sm.state = 'done' or sm.state IS NULL)
                    AND (sm.scrapped != 't' or sm.scrapped IS NULL)
                GROUP BY
                    mo.id
            ) comp_cost ON comp_cost.mo_id = mo.id
            LEFT JOIN (
                SELECT
                    mo_id                                                                    AS mo_id,
                    SUM(op_costs_hour / 60. * op_duration)                                   AS total,
                    SUM(op_duration)                                                         AS total_duration
                FROM (
                    SELECT
                        mo.id AS mo_id,
                        CASE
                            WHEN wo.costs_hour != 0.0 AND wo.costs_hour IS NOT NULL THEN wo.costs_hour
                            WHEN wc.costs_hour IS NOT NULL THEN wc.costs_hour
                            ELSE 0.0 END                                                                AS op_costs_hour,
                        CASE WHEN SUM(t.duration) IS NULL THEN 0.0 ELSE SUM(t.duration) END             AS op_duration
                    FROM mrp_production AS mo
                    LEFT JOIN mrp_workorder wo ON wo.production_id = mo.id
                    LEFT JOIN mrp_workcenter_productivity t ON t.workorder_id = wo.id
                    LEFT JOIN mrp_workcenter wc ON wc.id = t.workcenter_id
                    WHERE mo.state = 'done'
                    GROUP BY
                        mo.id,
                        wc.costs_hour,
                        wo.id
                    ) AS op_cost_vars
                GROUP BY mo_id
            ) op_cost ON op_cost.mo_id = mo.id
            LEFT JOIN (
                SELECT
                    mo.id AS mo_id,
                    CASE WHEN SUM(sm.cost_share) IS NOT NULL THEN SUM(sm.cost_share) / 100. ELSE 0.0 END AS byproduct_cost_share
                FROM stock_move AS sm
                LEFT JOIN mrp_production AS mo ON sm.production_id = mo.id
                WHERE
                    mo.state = 'done'
                    AND sm.state = 'done'
                    AND sm.product_qty != 0
                    AND sm.scrapped != 't'
                GROUP BY mo.id
            ) cost_share ON cost_share.mo_id = mo.id
            LEFT JOIN (
                SELECT
                    mo.id AS mo_id,
                    SUM(sm.product_qty) AS product_qty
                FROM stock_move AS sm
                RIGHT JOIN mrp_production AS mo ON sm.production_id = mo.id
                 WHERE
                    mo.state = 'done'
                    AND sm.state = 'done'
                    AND sm.product_qty != 0
                    AND mo.product_id = sm.product_id
                GROUP BY mo.id
            ) prod_qty ON prod_qty.mo_id = mo.id
            LEFT JOIN {currency_table} ON currency_table.company_id = mo.company_id
        """.format(
            currency_table=self.env['res.currency']._get_query_currency_table({'multi_company': True, 'date': {'date_to': fields.Date.today()}}),
        )

        return from_str

    def _where(self):
        where_str = """
            WHERE
                mo.state = 'done'
        """

        return where_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                mo.id,
                cost_share.byproduct_cost_share,
                comp_cost.total,
                op_cost.total,
                op_cost.total_duration,
                prod_qty.product_qty,
                currency_table.rate
        """

        return group_by_str
