# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', company_dependent=True,
        help="Analytic account in which cost and revenue entries will take place for financial management of the manufacturing order.")
