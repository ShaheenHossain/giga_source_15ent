# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models

class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    task_ids = fields.Many2many('project.task', string='Tasks')
