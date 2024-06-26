# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models, api, _
from giga.exceptions import UserError
from giga.tools.sql import column_exists, create_column



class AccountMove(models.Model):
    _inherit = 'account.move'

    def _auto_init(self):
        if not column_exists(self.env.cr, "account_move", "l10n_es_reports_mod349_available"):
            create_column(self.env.cr, "account_move", "l10n_es_reports_mod349_available", "bool")
            mod349_countries = self.env.ref('base.europe').country_ids - self.env.ref('base.es')
            if mod349_countries:
                self.env.cr.execute(
                    """
                        UPDATE account_move
                        SET l10n_es_reports_mod349_available = true
                        FROM res_partner partner
                        WHERE partner.id = account_move.partner_id
                        AND partner.country_id IN %s
                    """, [tuple(mod349_countries.ids)]
                )
        return super()._auto_init()

    def _default_mod_349_invoice_type(self):
        invoice_type = self.env.context.get('move_type', False)

        if invoice_type == 'in_invoice':
            return 'A'
        if invoice_type == 'out_invoice':
            return 'E'

    def _mod_349_selection_values(self):
        context = self.env.context
        if context.get('move_type') in self.get_sale_types():
            return[('E', _("E - Supply")), ('T', _("T - Triangular Operation")), ('S', _("S - Services sale")), ('M', _("M - Supply without taxes")), ('H', _("H - Supply without taxes delivered by a legal representative"))]
        if context.get('move_type') in self.get_purchase_types():
            return [('A', _("A - Acquisition")), ('T', _("T - Triangular Operation")), ('I', _("I - Services acquisition"))]
        # If no type is given in context, we give access to every possible value for the field
        return [('A', _("A - Acquisition")), ('E', _("E - Supply")), ('T', _("T - Triangular Operation")), ('S', _("S - Services sale")), ('I', _("I - Services acquisition")), ('M', _("M - Supply without taxes")), ('H', _("H - Supply without taxes delivered by a legal representative"))]

    l10n_es_reports_mod347_invoice_type = fields.Selection(string="Type for mod 347", selection=[('regular', "Regular operation"), ('insurance', "Insurance operation")], default='regular', help="Defines the category into which this invoice falls for mod 347 report.")
    l10n_es_reports_mod349_invoice_type = fields.Selection(string="Type for mod 349", selection="_mod_349_selection_values", help="Defines the category into which this invoice falls for mod 349 report", default=_default_mod_349_invoice_type)
    l10n_es_reports_mod349_available = fields.Boolean(string="Available for Mod349", store=True, compute="_compute_l10n_es_reports_mod349_available", help="True if and only if the invoice must be reported on mod 349 report, i.e. it concerns an intracommunitary operation.")

    @api.depends('partner_id.country_id')
    def _compute_l10n_es_reports_mod349_available(self):
        # Mod 349 is required for all european countries, except Spain
        mod349_countries = self.env.ref('base.europe').country_ids.filtered_domain([('code', '!=', 'ES')])
        for record in self:
            record.l10n_es_reports_mod349_available = record.partner_id.country_id in mod349_countries

    def _post(self, soft=True):
        """ Overridden to require Spanish invoice type to be set if the company
        of the invoice uses a Spanish COA (so other companies using other COA
        on the same DB won't be force to use them).
        """
        posted = super()._post(soft)
        spanish_coa_list = [
            self.env.ref('l10n_es.account_chart_template_pymes'),
            self.env.ref('l10n_es.account_chart_template_assoc'),
            self.env.ref('l10n_es.account_chart_template_full'),
        ]
        for record in posted.filtered(lambda move: move.is_invoice()):
            if record.company_id.chart_template_id in spanish_coa_list and \
            record.partner_id.country_id.code == "ES" and \
            (not record.l10n_es_reports_mod347_invoice_type or (record.l10n_es_reports_mod349_available and not record.l10n_es_reports_mod349_invoice_type)):
                raise UserError(_("Please select a Spanish invoice type for this invoice."))
        return posted

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if not res.l10n_es_reports_mod349_invoice_type:
            res.l10n_es_reports_mod349_invoice_type = res.with_context(move_type=res.move_type)._default_mod_349_invoice_type()
        return res
