from psycopg2 import sql

from giga import fields, models, tools


class HrWorkEntryReport(models.Model):
    _name = 'hr.work.entry.report'
    _description = 'Work Entries Analysis Report'
    _auto = False
    _order = 'date_start desc'

    number_of_days = fields.Float('Days', readonly=True)

    date_start = fields.Datetime('Date Start', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    department_id = fields.Many2one('hr.department', 'Department', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True)
    work_entry_type_id = fields.Many2one('hr.work.entry.type', 'Work Entry Type', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('conflict', 'Conflict'),
        ('cancelled', 'Cancelled')
    ], readonly=True)

    def init(self):
        query = """
        SELECT
            we.id,
            we.date_start,
            we.work_entry_type_id,
            we.employee_id,
            we.department_id,
            we.company_id,
            we.state,
            we.duration / work_schedule.hours_per_day AS number_of_days
        FROM (
            SELECT
                id,
                employee_id,
                contract_id,
                date_start,
                date_stop,
                work_entry_type_id,
                department_id,
                company_id,
                state,
                duration
            FROM
                hr_work_entry
            WHERE
                employee_id IS NOT NULL
                AND employee_id IN (SELECT id FROM hr_employee)
                AND active = TRUE
        ) we
        LEFT JOIN (
            SELECT
                contract.id AS contract_id,
                resource_calendar_id,
                hours_per_day
            FROM
                hr_contract contract
            LEFT JOIN (
                SELECT
                    id,
                    hours_per_day
                FROM
                    resource_calendar
            ) calendar ON calendar.id = contract.resource_calendar_id
        ) work_schedule ON we.contract_id = work_schedule.contract_id
        """

        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            sql.SQL("CREATE or REPLACE VIEW {} as ({})").format(
                sql.Identifier(self._table),
                sql.SQL(query)
            ))
