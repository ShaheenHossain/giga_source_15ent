# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, fields, api

from giga.exceptions import ValidationError

from giga.addons.base_iban.models.res_partner_bank import validate_iban
from giga.addons.base.models.res_bank import sanitize_account_number


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_reference_model = fields.Selection(selection_add=[
        ('ch', 'Switzerland')
    ], ondelete={'ch': lambda recs: recs.write({'invoice_reference_model': 'giga'})})
