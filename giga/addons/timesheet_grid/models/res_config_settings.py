# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.


from giga import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reminder_user_allow = fields.Boolean("Employee Reminder", related='company_id.timesheet_mail_employee_allow', readonly=False,
        help="If checked, send an email to all users who have not recorded their timesheet")
    reminder_user_delay = fields.Integer("Days to Remind User", related='company_id.timesheet_mail_employee_delay', readonly=False)
    reminder_user_interval = fields.Selection(string='User Reminder Frequency', required=True,
        related='company_id.timesheet_mail_employee_interval', readonly=False)

    reminder_manager_allow = fields.Boolean("Manager Reminder", related='company_id.timesheet_mail_manager_allow', readonly=False,
        help="If checked, send an email to all manager")
    reminder_manager_delay = fields.Integer("Days to Remind Manager", related='company_id.timesheet_mail_manager_delay', readonly=False)
    reminder_manager_interval = fields.Selection(string='Manager Reminder Frequency', required=True,
        related='company_id.timesheet_mail_manager_interval', readonly=False)
    timesheet_min_duration = fields.Integer('Minimal Duration', default=15, config_parameter='timesheet_grid.timesheet_min_duration')
    timesheet_rounding = fields.Integer('Round up', default=15, config_parameter='timesheet_grid.timesheet_rounding')
