# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, tools


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    last_appraisal_id = fields.Many2one(readonly=True)
