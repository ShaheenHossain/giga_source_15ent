# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    module_pos_iot = fields.Boolean('IoT Box', related="is_posbox")
