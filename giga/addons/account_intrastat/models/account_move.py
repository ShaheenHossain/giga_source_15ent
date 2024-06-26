# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models
from giga.tools.sql import column_exists, create_column


class AccountMove(models.Model):
    _inherit = 'account.move'

    intrastat_transport_mode_id = fields.Many2one('account.intrastat.code', string='Intrastat Transport Mode',
        readonly=True, states={'draft': [('readonly', False)]}, domain="[('type', '=', 'transport')]")
    intrastat_country_id = fields.Many2one('res.country', string='Intrastat Country',
        help='Intrastat country, arrival for sales, dispatch for purchases',
        readonly=True, states={'draft': [('readonly', False)]}, domain=[('intrastat', '=', True)])

    def _get_invoice_intrastat_country_id(self):
        ''' Hook allowing to retrieve the intrastat country depending of installed modules.
        :return: A res.country record's id.
        '''
        self.ensure_one()
        return self.partner_id.country_id.id

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        # OVERRIDE to set 'intrastat_country_id' depending of the partner's country.
        res = super(AccountMove, self)._onchange_partner_id()
        if self.partner_id.country_id.intrastat:
            self.intrastat_country_id = self._get_invoice_intrastat_country_id()
        else:
            self.intrastat_country_id = False
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _auto_init(self):
        if not column_exists(self.env.cr, "account_move_line", "intrastat_product_origin_country_id"):
            create_column(self.env.cr, "account_move_line", "intrastat_product_origin_country_id", "int4")
        return super()._auto_init()

    intrastat_transaction_id = fields.Many2one('account.intrastat.code', string='Intrastat', domain="[('type', '=', 'transaction')]")
    intrastat_product_origin_country_id = fields.Many2one('res.country', string='Product Country', compute='_compute_origin_country', store=True, readonly=False)

    @api.depends('product_id')
    def _compute_origin_country(self):
        for line in self:
            line.intrastat_product_origin_country_id = line.product_id.product_tmpl_id.intrastat_origin_country_id
