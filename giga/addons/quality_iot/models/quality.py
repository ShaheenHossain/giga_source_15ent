# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class QualityPoint(models.Model):
    _inherit = "quality.point"

    device_id = fields.Many2one('iot.device', ondelete='restrict', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
