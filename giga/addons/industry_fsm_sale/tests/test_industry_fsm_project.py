# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details

from psycopg2 import IntegrityError

from giga.tests import tagged
from giga.tools import mute_logger
from giga.tests.common import Form

from .common import TestFsmFlowSaleCommon


@tagged('-at_install', 'post_install')
class TestIndustryFsmProject(TestFsmFlowSaleCommon):

    def test_timesheet_product_is_required(self):
        """ Test if timesheet product is required in billable fsm project

            To do this we need to check if an exception is raise when the timesheet
            product is False/None and the project config has this props:
                - allow_billable=True,
                - allow_timesheets=True,
                - is_fsm=True.

            Test Case:
            =========
            Remove the timesheet product in the billable fsm project and check if an exception is raise.
        """
        with mute_logger('giga.sql_db'):
            with self.assertRaises(IntegrityError):
                self.fsm_project.write({'timesheet_product_id': False})
                self.fsm_project.flush()

    def test_convert_project_into_fsm_project(self):
        """ Test when we want to convert a project to fsm project

            Normally, this project should be billable and its pricing type should be task_rate.

            Test Case:
            =========
            1) Convert a non billable project to a fsm project and check if
                - allow_billable=True,
                - pricing_type="task_rate",
                - is_fsm=True,
                - allow_material=True,
            2) Convert a project with pricing_type="employee_rate"
            3) Convert a project with pricing_type="project_rate"
        """
        # 1) Convert a non billable project to a fsm project
        self.project_non_billable.write({'is_fsm': True})
        self.assertTrue(self.project_non_billable.allow_billable)
        self.assertTrue(self.project_non_billable.is_fsm)
        self.assertTrue(self.project_non_billable.allow_material)
        self.assertEqual(self.project_non_billable.pricing_type, 'task_rate')

        # 2) Convert a project with pricing_type="employee_rate"
        # Configuration of the employee rate project before convert it into fsm project
        self.project_employee_rate = self.project_task_rate.copy({
            'name': 'Project with pricing_type="employee_rate"',
            'sale_line_id': self.so.order_line[0].id,
            'sale_line_employee_ids': [(0, 0, {
                'employee_id': self.employee_user.id,
                'sale_line_id': self.so.order_line[1].id,
            })]
        })
        # Convert the project into fsm project
        self.project_employee_rate.write({'is_fsm': True})
        # Check if the configuration is the one expected
        self.assertTrue(self.project_employee_rate.is_fsm)
        self.assertTrue(self.project_employee_rate.allow_material)
        self.assertEqual(self.project_employee_rate.pricing_type, 'employee_rate')
        self.assertFalse(self.project_employee_rate.sale_order_id)
        self.assertFalse(self.project_employee_rate.sale_line_id)

        # 3) Convert a project with pricing_type="project_rate"
        # Configuration of the "project rate" project before convert it into fsm project
        self.project_project_rate = self.project_task_rate.copy({
            'name': 'Project with pricing_type="project_rate"',
            'sale_line_id': self.so.order_line[1].id,
        })
        self.project_project_rate.write({'is_fsm': True})
        self.assertTrue(self.project_project_rate.is_fsm)
        self.assertTrue(self.project_project_rate.allow_material)
        self.assertEqual(self.project_project_rate.pricing_type, 'task_rate')
        self.assertFalse(self.project_project_rate.sale_order_id)
        self.assertFalse(self.project_project_rate.sale_line_id)

    def test_fsm_project_form_view(self):
        """ Test if in the form view of the fsm project, the user can always edit the price unit in the mapping

            Test Case:
            =========
            1) Use the Form class to create a fsm project with a form view
            2) Define this project as fsm project (is_fsm = True)
            3) Create an employee mapping in this project
            4) Check if the _compute_price_unit set the correct price unit
            5) Change manually the price unit in this mapping and check if the edition is correctly done as expected
            6) Save the creation and check the value in the pricing_type, partner_id and employee mapping price_unit fields.
        """
        with Form(self.env['project.project'].with_context({'tracking_disable': True})) as project_form:
            project_form.name = 'Test Fsm Project'
            project_form.is_fsm = True
            with project_form.sale_line_employee_ids.new() as mapping_form:
                mapping_form.employee_id = self.employee_manager
                mapping_form.timesheet_product_id = self.product_order_timesheet1
                self.assertEqual(mapping_form.price_unit, self.product_order_timesheet1.lst_price, 'The price unit should be computed and equal to the price unit defined in the timesheet product.')
                mapping_form.price_unit = 150
                self.assertNotEqual(mapping_form.price_unit, self.product_order_timesheet1.lst_price, 'The price unit should be the one selected by the user and no longer the one defined in the timesheet product.')
                self.assertEqual(mapping_form.price_unit, 150, 'The price should be equal to 150.')
            project = project_form.save()
            self.assertEqual(project.pricing_type, 'employee_rate', 'The pricing type of this project should be equal to employee rate since it has a mapping.')
            self.assertFalse(project.partner_id, 'No partner should be set with the compute_partner_id because this compute should be ignored in a fsm project.')
            self.assertEqual(project.sale_line_employee_ids.price_unit, 150, 'The price unit should remain to 150.')
