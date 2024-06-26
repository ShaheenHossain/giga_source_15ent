# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, _


class hr_department(models.Model):
    _inherit = 'hr.department'

    appraisals_to_process_count = fields.Integer(compute='_compute_appraisals_to_process', string='Appraisals to Process')
    employee_feedback_template = fields.Html(
        compute='_compute_appraisal_feedbacks', store=True, readonly=False)
    manager_feedback_template = fields.Html(
        compute='_compute_appraisal_feedbacks', store=True, readonly=False)
    custom_appraisal_templates = fields.Boolean(string="Custom Appraisal Templates", default=False)

    def _compute_appraisals_to_process(self):
        appraisals = self.env['hr.appraisal'].read_group(
            [('department_id', 'in', self.ids), ('state', 'in', ['new', 'pending'])], ['department_id'], ['department_id'])
        result = dict((data['department_id'][0], data['department_id_count']) for data in appraisals)
        for department in self:
            department.appraisals_to_process_count = result.get(department.id, 0)

    @api.depends('company_id')
    def _compute_appraisal_feedbacks(self):
        for department in self:
            department.employee_feedback_template = department.company_id.appraisal_employee_feedback_template or self.env.company.appraisal_employee_feedback_template
            department.manager_feedback_template = department.company_id.appraisal_manager_feedback_template or self.env.company.appraisal_manager_feedback_template
