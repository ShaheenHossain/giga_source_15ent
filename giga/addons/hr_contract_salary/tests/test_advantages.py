# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from unittest.mock import patch

from giga.fields import Date, Datetime
from giga.tests.common import TransactionCase
from dateutil.relativedelta import relativedelta
from giga.addons.hr_contract_salary.models.hr_contract import HrContract


class TestAdvantages(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': "John"})
        cls.structure_type = cls.env['hr.payroll.structure.type'].create({'name': 'struct'})
        cls.contract = cls.env['hr.contract'].create({
            'name': "Contract",
            'employee_id': cls.employee.id,
            'wage': 6500,
            'structure_type_id': cls.structure_type.id,
        })

    def test_yearly_cost_new_advantage(self):
        fieldname = 'x_test_field'
        model = self.env.ref('hr_contract.model_hr_contract')
        field = self.env['ir.model.fields'].create({
            'name': fieldname,
            'model': model.name,
            'ttype': 'float',
            'model_id': model.id,
        })
        self.contract.write({fieldname: 50})
        self.assertEqual(self.contract.final_yearly_costs, 12 * self.contract.wage)
        advantage_costs = HrContract._get_advantages_costs
        with patch.object(HrContract, '_get_advantages_costs', lambda self: advantage_costs(self) + self[fieldname]):
            atype = self.env['hr.contract.salary.advantage.type'].create({})
            self.env['hr.contract.salary.advantage'].create({
                'impacts_net_salary': True,
                'advantage_type_id': atype.id,
                'res_field_id': field.id,
                'cost_res_field_id': field.id,
                'structure_type_id': self.structure_type.id,
            })
        self.assertEqual(self.contract.final_yearly_costs, 12 * (self.contract.wage + 50), "The new advantage should have updated the yearly cost")

    def test_holidays_yearly_cost(self):
        # yearly cost should not change even if the number of extra time off changes
        with patch.object(HrContract, '_get_advantages_costs', lambda self: 250):
            self.contract._compute_final_yearly_costs()
            base_yearly_cost = self.contract.final_yearly_costs
            self.contract.holidays = 15
            # this is triggered when configuring/signing a contract
            # and recomputes the final_yearly_costs field
            self.contract.wage_with_holidays = 6076.57
            self.assertAlmostEqual(base_yearly_cost, self.contract.final_yearly_costs, 2,
                'Yearly costs should stay the same')