# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_holidays = fields.Float(string="Paid Time Off", default_model="hr.contract")
