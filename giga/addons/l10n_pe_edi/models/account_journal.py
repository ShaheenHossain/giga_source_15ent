
# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.depends('l10n_latam_use_documents')
    def _compute_edi_format_ids(self):
        # Add the dependency to l10n_latam_use_documents used by '_is_compatible_with_journal'
        return super()._compute_edi_format_ids()
