# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_reference_model = fields.Selection(selection_add=[
        ('be', 'Belgium')
        ], ondelete={'be': lambda recs: recs.write({'invoice_reference_model': 'giga'})})
