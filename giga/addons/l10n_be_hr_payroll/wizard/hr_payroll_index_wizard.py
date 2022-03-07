# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import _, api, fields, models
from giga.exceptions import UserError
from giga.tools import format_date


class HrPayrollIndex(models.TransientModel):
    _inherit = 'hr.payroll.index'

    @api.model
    def _index_wage(self, contract):
        super(HrPayrollIndex, self)._index_wage(contract)
        if contract._get_work_time_rate() == 0:
            time_credit_full_time_wage = contract['time_credit_full_time_wage']
            contract.write({'time_credit_full_time_wage': time_credit_full_time_wage * (1 + self.percentage)})
