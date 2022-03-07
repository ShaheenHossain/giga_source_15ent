# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import api, fields, models
from giga.exceptions import UserError
from giga.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_delivery_line(self, carrier, price_unit):
        res = super(SaleOrder, self)._create_delivery_line(carrier, price_unit)
        if carrier.delivery_type == 'ups' and carrier.ups_bill_my_account:
            res.name = '[UPS] UPS Billing will remain to the customer'
        return res

    partner_ups_carrier_account = fields.Char(copy=False, compute='_compute_ups_carrier_account', inverse='_inverse_ups_carrier_account', readonly=False, string="UPS account number")
    ups_bill_my_account = fields.Boolean(related='carrier_id.ups_bill_my_account', readonly=True)

    @api.depends('partner_id')
    def _compute_ups_carrier_account(self):
        for order in self:
            order.partner_ups_carrier_account = order.partner_id.with_company(order.company_id).property_ups_carrier_account

    def _inverse_ups_carrier_account(self):
        for order in self:
            order.partner_id.with_company(order.company_id).property_ups_carrier_account = order.partner_ups_carrier_account

    def _action_confirm(self):
        if self.carrier_id.ups_bill_my_account and not self.partner_ups_carrier_account:
            raise UserError(_('You must enter an UPS account number.'))
        super(SaleOrder, self)._action_confirm()