# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import models, fields


class L10nLatamIdentificationType(models.Model):

    _inherit = "l10n_latam.identification.type"

    l10n_pe_vat_code = fields.Char()
