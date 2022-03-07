# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_cl_dte_email = fields.Char(string='DTE Email')
    l10n_cl_activity_description = fields.Char(string='Activity Description')

    def _l10n_cl_is_foreign(self):
        return self.country_id.code != "CL"
