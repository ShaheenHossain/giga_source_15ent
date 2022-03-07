# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, _
from giga.exceptions import ValidationError

class Company(models.Model):
    _inherit = 'res.company'

    hr_contract_timeoff_auto_allocation = fields.Boolean(string="Extra Time Off Allocation on contract signature")
    hr_contract_timeoff_auto_allocation_type_id = fields.Many2one(
        'hr.leave.type', string="Time Off Type", domain=[('has_valid_allocation', '=', True)])

    _sql_constraints = [
        ('auto_allocation',
            "CHECK(hr_contract_timeoff_auto_allocation = 'f' OR hr_contract_timeoff_auto_allocation_type_id IS NOT NULL)",
            "A Time Off Type is required once the Extra Time Off automatic allocation is set."),
    ]
