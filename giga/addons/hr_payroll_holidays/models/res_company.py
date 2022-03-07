# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    deferred_time_off_manager = fields.Many2one('res.users')
