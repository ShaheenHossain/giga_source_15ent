# coding: utf-8
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    l10n_mx_edi_code = fields.Char(
        'Code MX', help='Country code defined by the SAT in the catalog to '
        'CFDI version 3.3 and new complements. Will be used in the CFDI '
        'to indicate the country reference.')
