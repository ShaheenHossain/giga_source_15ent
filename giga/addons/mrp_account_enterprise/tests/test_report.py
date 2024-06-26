# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from giga.addons.mrp_account.tests.test_mrp_account import TestMrpAccount
from giga.tests.common import Form


class TestReportsCommon(TestMrpAccount):

    def test_mrp_cost_structure(self):
        """ Check that values of mrp_cost_structure are correctly calculated even when:
        1. byproducts with a cost share.
        2. multi-company + multi-currency environment.
        """

        # create MO with component cost + operations cost
        self.product_table_sheet.standard_price = 20.0
        self.product_table_leg.standard_price = 5.0
        self.product_bolt.standard_price = 1.0
        self.product_screw.standard_price = 2.0
        self.product_table_leg.tracking = 'none'
        self.product_table_sheet.tracking = 'none'
        self.mrp_workcenter.costs_hour = 50.0

        bom = self.mrp_bom_desk.copy()
        production_table_form = Form(self.env['mrp.production'])
        production_table_form.product_id = self.dining_table
        production_table_form.bom_id = bom
        production_table_form.product_qty = 1
        production_table = production_table_form.save()

        # add a byproduct w/ a non-zero cost share
        byproduct_cost_share = 10
        byproduct = self.env['product.product'].create({
            'name': 'Plank',
            'type': 'product',
        })

        self.env['stock.move'].create({
            'name': "Byproduct",
            'product_id': byproduct.id,
            'product_uom': byproduct.uom_id.id,
            'product_uom_qty': 1,
            'production_id': production_table.id,
            'location_id': self.ref('stock.stock_location_stock'),
            'location_dest_id': self.ref('stock.stock_location_output'),
            'cost_share': byproduct_cost_share
        })

        production_table.action_confirm()
        mo_form = Form(production_table)
        mo_form.qty_producing = 1
        production_table = mo_form.save()

        # add operation duration otherwise 0 operation cost
        self.env['mrp.workcenter.productivity'].create({
            'workcenter_id': self.mrp_workcenter.id,
            'date_start': datetime.now() - timedelta(minutes=30),
            'date_end': datetime.now(),
            'loss_id': self.env.ref('mrp.block_reason7').id,
            'description': self.env.ref('mrp.block_reason7').name,
            'workorder_id': production_table.workorder_ids[0].id
        })

        # avoid qty done not being updated when enterprise mrp_workorder is installed
        for move in production_table.move_raw_ids:
            move.quantity_done = move.product_uom_qty
        production_table._post_inventory()
        production_table.button_mark_done()

        total_component_cost = sum(move.product_id.standard_price * move.quantity_done for move in production_table.move_raw_ids)
        total_operation_cost = sum(wo.costs_hour * sum(wo.time_ids.mapped('duration')) / 60.0 for wo in production_table.workorder_ids)

        report = self.env['report.mrp_account_enterprise.mrp_cost_structure']
        report.flush()  # flush to avoid the wo duration not being available in the db in order to correctly build report
        report_values = report._get_report_values(docids=production_table.id)['lines'][0]
        self.assertEqual(report_values['component_cost_by_product'][self.dining_table], total_component_cost * (100 - byproduct_cost_share) / 100)
        self.assertEqual(report_values['operation_cost_by_product'][self.dining_table], total_operation_cost * (100 - byproduct_cost_share) / 100)
        self.assertEqual(report_values['component_cost_by_product'][byproduct], total_component_cost * byproduct_cost_share / 100)
        self.assertEqual(report_values['operation_cost_by_product'][byproduct], total_operation_cost * byproduct_cost_share / 100)

        # create another company w/ different currency + rate
        exchange_rate = 4
        currency_p = self.env['res.currency'].create({
            'name': 'DBL',
            'symbol': 'DD',
            'rounding': 0.01,
            'currency_unit_label': 'Doubloon'
        })
        company_p = self.env['res.company'].create({'name': 'Pirates R Us', 'currency_id': currency_p.id})
        self.env['res.currency.rate'].create({
            'name': '2010-01-01',
            'rate': exchange_rate,
            'currency_id': self.env.company.currency_id.id,
            'company_id': company_p.id,
        })

        user_p = self.env['res.users'].create({
            'name': 'pirate',
            'login': 'pirate',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('mrp.group_mrp_manager').id])],
            'company_id': company_p.id,
            'company_ids': [(6, 0, [company_p.id, self.env.company.id])]
        })

        report_values = report.with_user(user_p)._get_report_values(docids=production_table.id)['lines'][0]
        self.assertEqual(report_values['component_cost_by_product'][self.dining_table], total_component_cost * (100 - byproduct_cost_share) / 100 / exchange_rate)
        self.assertEqual(report_values['operation_cost_by_product'][self.dining_table], total_operation_cost * (100 - byproduct_cost_share) / 100 / exchange_rate)
        self.assertEqual(report_values['component_cost_by_product'][byproduct], total_component_cost * byproduct_cost_share / 100 / exchange_rate)
        self.assertEqual(report_values['operation_cost_by_product'][byproduct], total_operation_cost * byproduct_cost_share / 100 / exchange_rate)
