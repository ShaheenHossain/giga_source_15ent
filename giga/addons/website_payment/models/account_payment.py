# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_donation = fields.Boolean(string="Is Donation", related="payment_transaction_id.is_donation", help="Is the payment a donation")
