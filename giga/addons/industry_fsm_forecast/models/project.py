# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models


class Project(models.Model):
    _inherit = 'project.project'

    allow_forecast = fields.Boolean(compute='_compute_allow_forecast', store=True, readonly=False)

    @api.depends('is_fsm')
    def _compute_allow_forecast(self):
        for project in self:
            if not project._origin:
                project.allow_forecast = not project.is_fsm
