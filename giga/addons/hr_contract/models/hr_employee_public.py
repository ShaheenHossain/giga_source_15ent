# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    first_contract_date = fields.Date(related='employee_id.first_contract_date', groups="base.group_user")
