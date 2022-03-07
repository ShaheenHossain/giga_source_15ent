# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models, api, _


class UomUom(models.Model):
    _inherit = 'uom.uom'

    l10n_cl_sii_code = fields.Char('SII Code')
