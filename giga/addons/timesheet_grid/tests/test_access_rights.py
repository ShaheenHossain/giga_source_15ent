from giga import fields

from giga.exceptions import AccessError, UserError

from giga.tests.common import new_test_user
from giga.addons.hr_timesheet.tests.test_timesheet import TestCommonTimesheet


class TestAccessRightsTimesheetGrid(TestCommonTimesheet):

    def setUp(self):
        super(TestAccessRightsTimesheetGrid, self).setUp()

        self.user_approver = new_test_user(self.env, 'user_approver', groups='hr_timesheet.group_hr_timesheet_approver')

        self.empl_approver = self.env['hr.employee'].create({
            'name': 'Empl Approver 1',
            'user_id': self.user_approver.id
        })

        self.user_approver2 = new_test_user(self.env, 'user_approver2', groups='hr_timesheet.group_hr_timesheet_approver')

        self.empl_approver2 = self.env['hr.employee'].create({
            'name': 'Empl Approver 2',
            'user_id': self.user_approver2.id
        })

        self.empl_employee.write({
            'timesheet_manager_id': self.user_approver.id
        })

        today = fields.Date.today()

        self.timesheet = self.env['account.analytic.line'].with_user(self.user_approver).create({
            'name': 'My timesheet 1',
            'project_id': self.project_customer.id,
            'task_id': self.task2.id,
            'date': today,
            'unit_amount': 2,
            'employee_id': self.empl_employee.id
        })

        self.user_employee3 = new_test_user(self.env, 'user_employee3', groups='hr_timesheet.group_hr_timesheet_user')

        self.empl_employee3 = self.env['hr.employee'].create({
            'name': 'User Empl Employee 3',
            'user_id': self.user_employee3.id,
            'timesheet_manager_id': self.user_approver.id
        })

        self.timesheet2 = self.env['account.analytic.line'].with_user(self.user_approver).create({
            'name': 'My timesheet 4',
            'project_id': self.project_customer.id,
            'task_id': self.task1.id,
            'date': today,
            'unit_amount': 2,
            'employee_id': self.empl_employee3.id
        })

        self.project_follower = self.env['project.project'].create({
            'name': "Project with visibility set on 'Invited employees'",
            'allow_timesheets': True,
            'privacy_visibility': 'followers',
        })
        # Prevent access right errors in test_access_rights_for_* methods
        self.project_follower.message_subscribe(partner_ids=[
            self.user_approver.partner_id.id, self.user_employee.partner_id.id, self.user_manager.partner_id.id
        ])

    def test_access_rights_for_employee(self):
        """ Check the operations of employee with the lowest access

            The employee with the lowest access rights can only :
                - read/write/create/delete his own timesheets
        """
        # Employee 1 create a timesheet for him
        timesheet_user1 = self.env['account.analytic.line'].with_user(self.user_employee).create({
            'project_id': self.project_customer.id,
            'task_id': self.task1.id,
            'name': 'timesheet for employee 1',
            'unit_amount': 1
        })

        with self.assertRaises(AccessError):
            # employee 2 want to read the timesheet of employee 1
            timesheet_user1.with_user(self.user_employee2).read([])

            # employee 2 want to modity the timesheet of employee 1
            timesheet_user1.with_user(self.user_employee2).write({
                'unit_amount': 0.5
            })

            # employee 2 want to unlink a timesheet of employee 1
            timesheet_user1.with_user(self.user_employee2).unlink()

            # employee 1 want to create a timesheet for employee 2
            self.env['account.analytic.line'].with_user(self.user_employee).create({
                'project_id': self.project_customer.id,
                'task_id': self.task1.id,
                'name': 'a second timesheet for employee 2',
                'unit_amount': 8,
                'employee_id': self.empl_employee2.id
            })

        # employee 1 update his timesheet
        timesheet_user1.with_user(self.user_employee).write({
            'unit_amount': 5
        })

        # check if the updating is correct
        self.assertEqual(timesheet_user1.unit_amount, 5)

        # employee 1 remove his timesheet
        timesheet_user1.with_user(self.user_employee).unlink()

    def test_access_rights_for_approver(self):
        """ Check the operations of the employee with the access rights 'approver'

            The approver can read/write/create/delete all timesheets.
        """
        # The approver can create a timesheet for a employee
        timesheet_user1 = self.env['account.analytic.line'].create({
            'project_id': self.project_customer.id,
            'task_id': self.task1.id,
            'name': 'timesheet for employee 1',
            'unit_amount': 1,
            'employee_id': self.empl_employee.id
        })

        # the approver can read the timesheet of employee 1
        res = timesheet_user1.with_user(self.user_approver).read(['name'])
        self.assertEqual(timesheet_user1.name, res[0]['name'])

        # the approver can update the timesheet of employee 1
        timesheet_user1.with_user(self.user_approver).write({
            'unit_amount': 5
        })
        self.assertEqual(timesheet_user1.unit_amount, 5)

        # the approver can delete the timesheet of employee 1
        timesheet_user1.with_user(self.user_approver).unlink()

    def test_access_rights_for_manager(self):
        """ Check the operations of the administrator

            The manager (administrator) can read/write/create/delete all
            timesheets.
        """
        # The manager can create a timesheet for a employee
        timesheet_user1 = self.env['account.analytic.line'].create({
            'project_id': self.project_customer.id,
            'task_id': self.task1.id,
            'name': 'timesheet for employee 1',
            'unit_amount': 1,
            'employee_id': self.empl_employee.id
        })

        # the manager can read the timesheet of employee 1
        res = timesheet_user1.with_user(self.user_manager).read(['name'])
        self.assertEqual(timesheet_user1.name, res[0]['name'])

        # the manager can update the timesheet of employee 1
        timesheet_user1.with_user(self.user_manager).write({
            'unit_amount': 5
        })
        self.assertEqual(timesheet_user1.unit_amount, 5)

        # the manager can delete the timesheet of employee 1
        timesheet_user1.with_user(self.user_manager).unlink()

    def test_timesheet_validation_approver(self):
        """ Check if the approver who has created the timesheet for an employee, can validate the timesheet."""
        timesheet_to_validate = self.timesheet
        timesheet_to_validate.with_user(self.user_approver).action_validate_timesheet()
        self.assertEqual(timesheet_to_validate.validated, True)

    def test_timesheet_validation_by_approver_when_he_is_not_responsible(self):
        """Check if an approver can validate an timesheet, if he isn't the Timesheet Responsible."""
        timesheet_to_validate = self.timesheet2

        # Normally the approver can't validate the timesheet because he doesn't know the project (and he isn't the manager of the employee) and he's not the Timesheet Responsible
        res = timesheet_to_validate.with_user(self.user_approver2).action_validate_timesheet()
        self.assertEqual(res['params']['type'], 'danger')
        self.assertEqual(timesheet_to_validate.validated, False)

    def test_timesheet_validation_by_approver_when_he_is_manager_of_employee(self):
        """Check if an approver can validate the timesheets into this project, when he is the manager of the employee."""
        timesheet_to_validate = self.timesheet2
        timesheet_to_validate.with_user(self.user_approver).action_validate_timesheet()
        self.assertEqual(timesheet_to_validate.validated, True)

    def test_show_timesheet_only_if_user_follow_project(self):
        """
            Test if the user cannot see the timesheets into a project when this project with visibility set on 'Invited employee', this user has the access right : 'See my timesheets' and he doesn't follow the project.
        """
        Timesheet = self.env['account.analytic.line']
        Partner = self.env['res.partner']
        partner = Partner.create({
            'name': self.user_manager.name,
            'email': self.user_manager.email
        })

        self.user_manager.write({
            'partner_id': partner.id
        })

        self.project_follower.message_subscribe(partner_ids=[self.user_manager.partner_id.id])

        timesheet = Timesheet.with_user(self.user_manager).create({
            'project_id': self.project_follower.id,
            'name': '/'
        })

        with self.assertRaises(AccessError):
            timesheet.with_user(self.user_employee).read()
            timesheet.with_user(self.user_approver).read()

    def test_employee_update_validated_timesheet(self):
        """
            Check an user with access right 'See own timesheet'
            cannot update his timesheet when it's validated.
        """
        timesheet_to_validate = self.timesheet
        timesheet_to_validate.with_user(self.user_approver).action_validate_timesheet()
        self.assertEqual(self.timesheet.validated, True)
        with self.assertRaises(AccessError):
            self.timesheet.with_user(self.user_employee).write({'unit_amount': 10})

        self.assertEqual(self.timesheet.unit_amount, 2)

    def test_employee_validate_timesheet(self):
        """
            Check an user with the lowest access right
            cannot validate any timesheets.
        """
        timesheet_to_validate = self.timesheet
        res = timesheet_to_validate.with_user(self.user_employee).action_validate_timesheet()
        self.assertEqual(res['params']['type'], 'danger')
        self.assertEqual(self.timesheet.validated, False)

    def test_employee_read_timesheet_of_other_employee(self):
        """ Check if the employee with the lowest access right
            cannot read timesheet of another employee
        """
        with self.assertRaises(AccessError):
            self.timesheet.with_user(self.user_employee3).read([])
            self.timesheet.with_user(self.user_employee2).read([])

        # the employee 1 can read this timesheet because his own
        res = self.timesheet.with_user(self.user_employee).read(['name'])
        self.assertEqual(res[0]['name'], 'My timesheet 1')
