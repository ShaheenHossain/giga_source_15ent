# -*- coding:utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, fields


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'
    _description = 'Salary Structure Type'

    salary_advantage_ids = fields.One2many('hr.contract.salary.advantage', 'structure_type_id')