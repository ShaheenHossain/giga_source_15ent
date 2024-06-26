# -*- coding:utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, _
from giga.exceptions import UserError


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'
    _description = 'Salary Structure Type'

    name = fields.Char('Structure Type')
    default_schedule_pay = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('semi-annually', 'Semi-annually'),
        ('annually', 'Annually'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-weekly'),
        ('bi-monthly', 'Bi-monthly'),
    ], string='Default Scheduled Pay', default='monthly',
    help="Defines the frequency of the wage payment.")
    struct_ids = fields.One2many('hr.payroll.structure', 'type_id', string="Structures")
    default_struct_id = fields.Many2one('hr.payroll.structure', string="Regular Pay Structure")
    default_work_entry_type_id = fields.Many2one('hr.work.entry.type', help="Work entry type for regular attendances.", required=True,
                                                 default=lambda self: self.env.ref('hr_work_entry.work_entry_type_attendance', raise_if_not_found=False))
    wage_type = fields.Selection([('monthly', 'Monthly Fixed Wage'), ('hourly', 'Hourly Wage')], default='monthly', required=True)
    struct_type_count = fields.Integer(compute='_compute_struct_type_count', string='Structure Type Count')

    def _compute_struct_type_count(self):
        for structure_type in self:
            structure_type.struct_type_count = len(structure_type.struct_ids)

    def _check_country(self, vals):
        country_id = vals.get('country_id')
        if country_id and country_id not in self.env.companies.mapped('country_id').ids:
            raise UserError(_('You should also be logged into a company in %s to set this country.', self.env['res.country'].browse(country_id).name))

    def write(self, vals):
        if self.env.context.get('payroll_check_country'):
            self._check_country(vals)
        return super().write(vals)

    @api.model
    def create(self, vals):
        if self.env.context.get('payroll_check_country'):
            self._check_country(vals)
        return super().create(vals)
