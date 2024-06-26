# -*- coding:utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from datetime import date

from giga.tests import tagged
from giga.exceptions import ValidationError

from .common import TestPayrollCommon


@tagged('post_install_l10n', 'post_install', '-at_install', 'payroll_credit_time')
class TestPayrollCreditTime(TestPayrollCommon):

    def setUp(self):
        super(TestPayrollCreditTime, self).setUp()

        today = date.today()
        self.paid_time_off_type = self.holiday_leave_types #self.holiday_leave_types.filtered(lambda leave_type: leave_type.validity_start == date(today.year, 1, 1) and leave_type.validity_stop == date(today.year, 12, 31))

        self.wizard = self.env['hr.payroll.alloc.paid.leave'].create({
            'year': today.year - 1,
            'holiday_status_id': self.paid_time_off_type.id
        })
        self.wizard._onchange_struct_id()
        self.wizard.alloc_employee_ids = self.wizard.alloc_employee_ids.filtered(lambda alloc_employee: alloc_employee.employee_id.id in [self.employee_georges.id, self.employee_john.id, self.employee_a.id])

        view = self.wizard.generate_allocation()
        self.allocations = self.env['hr.leave.allocation'].search(view['domain'])
        for allocation in self.allocations:
            allocation.action_confirm()
            allocation.action_validate()

    def test_credit_time_for_georges(self):
        """
        Test Case:
        The employee Georges asks a credit time to work at mid-time (3 days/week) from 01/02 to 30/04 in the current year,
        normally, he has 14.5 days before his credit and with the credit, the number of paid time off days dereases
        9 days. If Georges didn't take some leaves during his credit, when he exists it, his number of paid time off
        days increase to the number of days he had before.
        """
        current_year = date.today().year

        georges_current_contract = self.georges_contracts[-1]
        georges_allocation = self.allocations.filtered(lambda alloc: alloc.employee_id.id == self.employee_georges.id)

        # Test for employee Georges
        # Credit time for Georges
        wizard = self.env['l10n_be.hr.payroll.schedule.change.wizard'].with_context(allowed_company_ids=self.belgian_company.ids, active_id=georges_current_contract.id).new({
            'date_start': date(current_year, 2, 1),
            'date_end': date(current_year, 4, 30),
            'resource_calendar_id': self.resource_calendar_mid_time.id,
            'leave_type_id': self.paid_time_off_type.id,
            'part_time': True,
        })
        self.assertEqual(wizard.time_off_allocation, 9)
        self.assertAlmostEqual(wizard.work_time_rate, 50, 2)
        self.assertEqual(wizard.leave_allocation_id.id, georges_allocation.id)
        view = wizard.with_context(force_schedule=True).action_validate()
        # Apply allocation changes directly
        self.env['l10n_be.schedule.change.allocation']._cron_update_allocation_from_new_schedule(date(current_year, 2, 1))
        self.assertEqual(georges_allocation.number_of_days, 9)

        # Apply allocation changes directly - Credit time exit
        full_time_contract = self.env['hr.contract'].search(view['domain']).filtered(lambda contract: not contract.time_credit and contract.id != georges_current_contract.id)
        self.env['l10n_be.schedule.change.allocation']._cron_update_allocation_from_new_schedule(full_time_contract.date_start)
        self.assertEqual(full_time_contract.time_credit, False)
        self.assertEqual(georges_allocation.number_of_days, 14.5)

    def test_credit_time_for_john_doe(self):
        """
        Test Case:
        The employee John Doe asks a credit time to work at 9/10 from 01/02 to 30/04 in the current year.
        """
        current_year = date.today().year
        john_current_contract = self.john_contracts[-1]
        john_allocation = self.allocations.filtered(lambda alloc: alloc.employee_id.id == self.employee_john.id)

        # Test for employee John Doe
        # Credit time for John Doe
        wizard = self.env['l10n_be.hr.payroll.schedule.change.wizard'].with_context(allowed_company_ids=self.belgian_company.ids, active_id=john_current_contract.id).new({
            'date_start': date(current_year, 2, 1),
            'date_end': date(current_year, 4, 30),
            'resource_calendar_id': self.resource_calendar_9_10.id,
            'leave_type_id': self.paid_time_off_type.id,
            'part_time': True,
        })
        self.assertEqual(wizard.time_off_allocation, 18) # 4*4*1 full days + 4*1*.5 half days
        self.assertAlmostEqual(wizard.work_time_rate, 90, 2)
        self.assertEqual(wizard.leave_allocation_id.id, john_allocation.id)
        view = wizard.with_context(force_schedule=True).action_validate()
        # Apply allocation changes directly
        self.env['l10n_be.schedule.change.allocation']._cron_update_allocation_from_new_schedule(date(current_year, 2, 1))
        self.assertEqual(john_allocation.number_of_days, 18)

        # Apply allocation changes directly - Credit time exit
        continuation_contract = self.env['hr.contract'].search(view['domain']).filtered(lambda contract: not contract.time_credit and contract.id != john_current_contract.id)
        self.env['l10n_be.schedule.change.allocation']._cron_update_allocation_from_new_schedule(continuation_contract.date_start)
        self.assertEqual(continuation_contract.time_credit, False)
        self.assertEqual(john_allocation.number_of_days, 10)

    def test_credit_time_for_a(self):
        """
        Test Case:
        The employee A has a contract full-time from 01/01 of the previous year.
        Then, he has right to 20 complete days as paid time off.
        The employee A asks a credit time to work at 4/5 (4 days/week) from 01/02 to 30/04 in the current year.
        With this credit time, his number of paid time off days decrease to
        """
        current_year = date.today().year
        a_current_contract = self.a_contracts[-1]
        a_allocation = self.allocations.filtered(lambda alloc: alloc.employee_id.id == self.employee_a.id)
        self.assertEqual(a_allocation.number_of_days, 20)

        # Test for employee A
        # Credit time for A
        wizard = self.env['l10n_be.hr.payroll.schedule.change.wizard'].with_context(allowed_company_ids=self.belgian_company.ids, active_id=a_current_contract.id).new({
            'date_start': date(current_year, 2, 1),
            'date_end': date(current_year, 4, 30),
            'resource_calendar_id': self.resource_calendar_4_5.id,
            'leave_type_id': self.paid_time_off_type.id,
            'part_time': True,
        })
        self.assertEqual(wizard.time_off_allocation, 16)
        self.assertAlmostEqual(wizard.work_time_rate, 80, 2)
        view = wizard.with_context(force_schedule=True).action_validate()
        self.env['l10n_be.schedule.change.allocation']._cron_update_allocation_from_new_schedule(date(current_year, 2, 1))

        # Apply allocation changes directly
        full_time_contract = self.env['hr.contract'].search(view['domain']).filtered(lambda contract: not contract.time_credit and contract.id != a_current_contract.id)
        self.env['l10n_be.schedule.change.allocation']._cron_update_allocation_from_new_schedule(full_time_contract.date_start)
        self.assertEqual(full_time_contract.time_credit, False)
        self.assertEqual(a_allocation.number_of_days, 20)

    def test_remaining_leaves_with_credit_time(self):
        """
        Test Case (only with the employee A)
        - Full Time from 01/01 to 31/05 and A took 6 days off (it remained 14 days)
        - 4/5 (4 days/week) from 01/06 to 31/08 and A took 6 days (it remained 5)
        - 1/2 (3 days/week) from 01/09 -> 31/12 (in this case, we need to do an exit credit to full time and then add a credit)
        """
        today = date.today()
        a_current_contract = self.a_contracts[-1]
        a_allocation = self.allocations.filtered(lambda alloc: alloc.employee_id.id == self.employee_a.id)

        leave = self.env['hr.leave'].create({
            'holiday_status_id': self.paid_time_off_type.id,
            'employee_id': self.employee_a.id,
            'request_date_from': date(today.year, 2, 1),
            'date_from': date(today.year, 2, 1),
            'date_to': date(today.year, 2, 6),
            'request_date_to': date(today.year, 2, 6),
            'number_of_days': 6
        })
        leave.action_validate()

        # Credit time
        wizard = self.env['l10n_be.hr.payroll.schedule.change.wizard'].with_context(allowed_company_ids=self.belgian_company.ids, active_id=a_current_contract.id).new({
            'date_start': date(today.year, 6, 1),
            'date_end': date(today.year, 8, 31),
            'resource_calendar_id': self.resource_calendar_4_5.id,
            'leave_type_id': self.paid_time_off_type.id,
            'part_time': True,
        })
        self.assertEqual(wizard.time_off_allocation, 17) #11 + 6 leaves taken
        self.assertAlmostEqual(wizard.work_time_rate, 80, 2)
        view = wizard.with_context(force_schedule=True).action_validate()

        # Apply allocation changes directly
        self.env['l10n_be.schedule.change.allocation']._cron_update_allocation_from_new_schedule(date(today.year, 6, 1))

        leave = self.env['hr.leave'].create({
            'holiday_status_id': self.paid_time_off_type.id,
            'employee_id': self.employee_a.id,
            'request_date_from': date(today.year, 7, 1),
            'date_from': date(today.year, 7, 1),
            'date_to': date(today.year, 7, 6),
            'request_date_to': date(today.year, 7, 6),
            'number_of_days': 6
        })
        leave.action_validate()

        # Apply allocation changes directly
        full_time_contract = self.env['hr.contract'].search(view['domain']).filtered(lambda contract: not contract.time_credit and contract.id != a_current_contract.id)
        self.env['l10n_be.schedule.change.allocation']._cron_update_allocation_from_new_schedule(full_time_contract.date_start)
        self.assertEqual(full_time_contract.time_credit, False)
        self.assertEqual(a_allocation.number_of_days, 18, "6 remained paid time offs and 12 days has been taken by the employee this current year")

        # Credit time
        wizard = self.env['l10n_be.hr.payroll.schedule.change.wizard'].with_context(allowed_company_ids=self.belgian_company.ids, active_id=full_time_contract.id).new({
            'date_start': date(today.year, 9, 2),
            'date_end': date(today.year, 12, 31),
            'resource_calendar_id': self.resource_calendar_mid_time.id,
            'leave_type_id': self.paid_time_off_type.id,
            'part_time': True,
        })
        self.assertEqual(wizard.time_off_allocation, 15)
        self.assertAlmostEqual(wizard.work_time_rate, 50, 2)
        view = wizard.with_context(force_schedule=True).action_validate()
        # Apply allocation changes directly
        self.env['l10n_be.schedule.change.allocation']._cron_update_allocation_from_new_schedule(date(today.year, 9, 2))

        # Normally he has already taken all his paid time offs, if he takes another, we should have an error
        with self.assertRaises(ValidationError):
            leave = self.env['hr.leave'].create({
                'holiday_status_id': self.paid_time_off_type.id,
                'employee_id': self.employee_a.id,
                'request_date_from': date(today.year, 10, 4),
                'date_from': date(today.year, 10, 4),
                'date_to': date(today.year, 10, 8),
                'request_date_to': date(today.year, 10, 8),
                'number_of_days': 5
            })
            leave.action_validate()
