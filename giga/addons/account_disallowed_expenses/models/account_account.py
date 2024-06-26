# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, fields


class AccountAccount(models.Model):
    _inherit = "account.account"

    disallowed_expenses_category_id = fields.Many2one('account.disallowed.expenses.category', string='Disallowed Expenses Category', domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]")
