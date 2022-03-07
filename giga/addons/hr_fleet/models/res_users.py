# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, fields


class User(models.Model):
    _inherit = ['res.users']

    employee_cars_count = fields.Integer(related='employee_id.employee_cars_count')

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['employee_cars_count']

    def action_get_claim_report(self):
        return self.employee_id.action_get_claim_report()

    def action_open_employee_cars(self):
        return self.employee_id.action_open_employee_cars()
