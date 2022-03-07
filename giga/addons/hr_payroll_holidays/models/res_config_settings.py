# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    deferred_time_off_manager = fields.Many2one('res.users', related='company_id.deferred_time_off_manager', readonly=False)
