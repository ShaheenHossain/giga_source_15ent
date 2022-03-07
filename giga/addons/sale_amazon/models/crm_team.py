# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    amazon_team = fields.Boolean(
        help="True if this sales team is associated with Amazon orders", default=False)
