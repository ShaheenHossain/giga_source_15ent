# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import datetime
import logging

from dateutil.relativedelta import relativedelta

from giga import api, fields, models, _
from giga.exceptions import UserError
from giga.tools.misc import format_date

_logger = logging.getLogger(__name__)

class HrAppraisal(models.Model):
    _name = "hr.appraisal"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Appraisal"
    _order = 'state desc, id desc'
    _rec_name = 'employee_id'
    _mail_post_access = 'read'

    def _get_default_employee(self):
        if self.env.context.get('active_model') in ('hr.employee', 'hr.employee.public') and 'active_id' in self.env.context:
            return self.env.context.get('active_id')
        elif self.env.context.get('active_model') == 'res.users' and 'active_id' in self.env.context:
            return self.env['res.users'].browse(self.env.context['active_id']).employee_id
        if not self.env.user.has_group('hr_appraisal.group_hr_appraisal_user'):
            return self.env.user.employee_id

    active = fields.Boolean(default=True)
    employee_id = fields.Many2one(
        'hr.employee', required=True, string='Employee', index=True,
        default=_get_default_employee)
    employee_user_id = fields.Many2one('res.users', string="Employee User", related='employee_id.user_id')
    company_id = fields.Many2one('res.company', related='employee_id.company_id', store=True)
    department_id = fields.Many2one(
        'hr.department', related='employee_id.department_id', string='Department', store=True)
    image_128 = fields.Image(related='employee_id.image_128')
    image_1920 = fields.Image(related='employee_id.image_1920')
    avatar_128 = fields.Image(related='employee_id.avatar_128')
    avatar_1920 = fields.Image(related='employee_id.avatar_1920')
    last_appraisal_id = fields.Many2one('hr.appraisal', related='employee_id.last_appraisal_id')
    last_appraisal_date = fields.Date(related='employee_id.last_appraisal_date')
    previous_appraisal_id = fields.Many2one('hr.appraisal')
    previous_appraisal_date = fields.Date(related='previous_appraisal_id.date_close', string='Previous Appraisal Date')
    uncomplete_goals_count = fields.Integer(related='employee_id.uncomplete_goals_count')
    employee_feedback_template = fields.Html(compute='_compute_feedback_templates')
    manager_feedback_template = fields.Html(compute='_compute_feedback_templates')

    date_close = fields.Date(
        string='Appraisal Date', help='Date of the appraisal, automatically updated when the appraisal is Done or Cancelled.', required=True, index=True,
        default=lambda self: datetime.date.today() + relativedelta(months=+1))
    state = fields.Selection(
        [('new', 'To Confirm'),
         ('pending', 'Confirmed'),
         ('done', 'Done'),
         ('cancel', "Cancelled")],
        string='Status', tracking=True, required=True, copy=False,
        default='new', index=True, group_expand='_group_expand_states')
    manager_ids = fields.Many2many(
        'hr.employee', 'appraisal_manager_rel', 'hr_appraisal_id',
        context={'active_test': False},
        domain="[('active', '=', 'True'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    manager_user_ids = fields.Many2many('res.users', string="Manager Users", compute='_compute_user_manager_rights')
    meeting_ids = fields.Many2many('calendar.event', string='Meetings')
    meeting_count_display = fields.Char(string='Meeting Count', compute='_compute_meeting_count')
    date_final_interview = fields.Date(string="Final Interview", compute='_compute_final_interview')
    is_implicit_manager = fields.Boolean(compute='_compute_user_manager_rights')
    is_appraisal_manager = fields.Boolean(compute='_compute_user_manager_rights')
    employee_autocomplete_ids = fields.Many2many('hr.employee', compute='_compute_user_manager_rights')
    waiting_feedback = fields.Boolean(
        string="Waiting Feedback from Employee/Managers", compute='_compute_waiting_feedback', tracking=True)
    employee_feedback = fields.Html(compute='_compute_employee_feedback', store=True, readonly=False)
    show_employee_feedback_full = fields.Boolean(compute='_compute_show_employee_feedback_full')
    manager_feedback = fields.Html(compute='_compute_manager_feedback', store=True, readonly=False)
    show_manager_feedback_full = fields.Boolean(compute='_compute_show_manager_feedback_full')
    employee_feedback_published = fields.Boolean(string="Employee Feedback Published", tracking=True)
    manager_feedback_published = fields.Boolean(string="Manager Feedback Published", tracking=True)
    can_see_employee_publish = fields.Boolean(compute='_compute_buttons_display')
    can_see_manager_publish = fields.Boolean(compute='_compute_buttons_display')
    assessment_note = fields.Many2one('hr.appraisal.note', string="Final Rating", help="This field is not visible to the Employee.", domain="[('company_id', '=', company_id)]")
    note = fields.Html(string="Private Note", help="The content of this note is not visible by the Employee.")
    appraisal_plan_posted = fields.Boolean()

    @api.depends('employee_id', 'manager_ids')
    def _compute_buttons_display(self):
        new_appraisals = self.filtered(lambda a: a.state == 'new')
        new_appraisals.update({
            'can_see_employee_publish': False,
            'can_see_manager_publish': False,
        })
        user_employee = self.env.user.employee_id
        is_manager = self.env.user.user_has_groups('hr_appraisal.group_hr_appraisal_user')
        for appraisal in self:
            appraisal.can_see_employee_publish = user_employee == appraisal.employee_id
            appraisal.can_see_manager_publish = user_employee.id in appraisal.manager_ids.ids
        for appraisal in self - new_appraisals:
            if is_manager and not appraisal.can_see_employee_publish and not appraisal.can_see_manager_publish:
                appraisal.can_see_employee_publish, appraisal.can_see_manager_publish = True, True

    @api.depends_context('uid')
    @api.depends('employee_id', 'manager_ids')
    def _compute_user_manager_rights(self):
        for appraisal in self:
            appraisal.manager_user_ids = appraisal.manager_ids.mapped('user_id')
        self.is_appraisal_manager = self.user_has_groups('hr_appraisal.group_hr_appraisal_user')
        if self.is_appraisal_manager:
            self.is_implicit_manager = False
            self.employee_autocomplete_ids = self.env['hr.employee'].search([('company_id', '=', self.env.company.id)])
        else:
            child_ids = self.env.user.employee_id.child_ids
            appraisal_child_ids = self.env.user.employee_id.appraisal_child_ids
            self.employee_autocomplete_ids = child_ids + appraisal_child_ids + self.env.user.employee_id
            self.is_implicit_manager = len(self.employee_autocomplete_ids) > 1

    @api.depends_context('uid')
    @api.depends('employee_id', 'employee_feedback_published')
    def _compute_show_employee_feedback_full(self):
        for appraisal in self:
            is_appraisee = appraisal.employee_id.user_id == self.env.user
            appraisal.show_employee_feedback_full = is_appraisee and not appraisal.employee_feedback_published

    @api.depends_context('uid')
    @api.depends('manager_ids', 'manager_feedback_published')
    def _compute_show_manager_feedback_full(self):
        for appraisal in self:
            is_appraiser = self.env.user in appraisal.manager_ids.user_id
            appraisal.show_manager_feedback_full = is_appraiser and not appraisal.manager_feedback_published

    @api.depends('department_id')
    def _compute_employee_feedback(self):
        for appraisal in self.filtered(lambda a: a.state == 'new'):
            appraisal.employee_feedback = appraisal.department_id.employee_feedback_template if appraisal.department_id.custom_appraisal_templates \
                else appraisal.company_id.appraisal_employee_feedback_template

    @api.depends('department_id')
    def _compute_manager_feedback(self):
        for appraisal in self.filtered(lambda a: a.state == 'new'):
            appraisal.manager_feedback = appraisal.department_id.manager_feedback_template if appraisal.department_id.custom_appraisal_templates \
                else appraisal.company_id.appraisal_manager_feedback_template

    @api.depends('department_id', 'company_id')
    def _compute_feedback_templates(self):
        for appraisal in self:
            appraisal.employee_feedback_template = appraisal.department_id.employee_feedback_template if appraisal.department_id.custom_appraisal_templates \
                else appraisal.company_id.appraisal_employee_feedback_template
            appraisal.manager_feedback_template = appraisal.department_id.manager_feedback_template if appraisal.department_id.custom_appraisal_templates \
                else appraisal.company_id.appraisal_manager_feedback_template

    @api.depends('employee_feedback_published', 'manager_feedback_published')
    def _compute_waiting_feedback(self):
        for appraisal in self:
            appraisal.waiting_feedback = not appraisal.employee_feedback_published or not appraisal.manager_feedback_published

    @api.depends('meeting_ids.start')
    def _compute_final_interview(self):
        today = fields.Date.today()
        with_meeting = self.filtered('meeting_ids')
        (self - with_meeting).date_final_interview = False
        for appraisal in with_meeting:
            all_dates = appraisal.meeting_ids.mapped('start')
            min_date, max_date = min(all_dates), max(all_dates)
            if min_date.date() >= today:
                appraisal.date_final_interview = min_date
            else:
                appraisal.date_final_interview = max_date

    @api.depends_context('lang')
    @api.depends('meeting_ids')
    def _compute_meeting_count(self):
        today = fields.Date.today()
        for appraisal in self:
            count = len(appraisal.meeting_ids)
            if not count:
                appraisal.meeting_count_display = _('No Meeting')
            elif count == 1:
                appraisal.meeting_count_display = _('1 Meeting')
            elif appraisal.date_final_interview >= today:
                appraisal.meeting_count_display = _('Next Meeting')
            else:
                appraisal.meeting_count_display = _('Last Meeting')

    def _group_expand_states(self, states, domain, order):
        return [key for key, val in self._fields['state'].selection]

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self = self.sudo()  # fields are not on the employee public
        if self.employee_id:
            self.manager_ids = self.employee_id.parent_id

    def subscribe_employees(self):
        for appraisal in self:
            partners = appraisal.manager_ids.mapped('related_partner_id') | appraisal.employee_id.related_partner_id
            appraisal.message_subscribe(partner_ids=partners.ids)

    def send_appraisal(self):
        for appraisal in self:
            confirmation_mail_template = appraisal.company_id.appraisal_confirm_mail_template
            mapped_data = {
                **{appraisal.employee_id: confirmation_mail_template},
                **{manager: confirmation_mail_template for manager in appraisal.manager_ids}
            }
            for employee, mail_template in mapped_data.items():
                if not employee.work_email or not self.env.user.email or not mail_template:
                    continue
                ctx = {
                    'employee_to_name': appraisal.employee_id.name,
                    'recipient_users': employee.user_id,
                    'url': '/mail/view?model=%s&res_id=%s' % ('hr.appraisal', appraisal.id),
                }
                mail_template = mail_template.with_context(**ctx)
                subject = mail_template._render_field('subject', appraisal.ids, post_process=False)[appraisal.id]
                body = mail_template._render_field('body_html', appraisal.ids, post_process=True)[appraisal.id]
                # post the message
                mail_values = {
                    'email_from': self.env.user.email_formatted,
                    'author_id': self.env.user.partner_id.id,
                    'model': None,
                    'res_id': None,
                    'subject': subject,
                    'body_html': body,
                    'auto_delete': True,
                    'email_to': employee.work_email
                }
                try:
                    template = self.env.ref('mail.mail_notification_light', raise_if_not_found=True)
                except ValueError:
                    _logger.warning('QWeb template mail.mail_notification_light not found when sending appraisal confirmed mails. Sending without layouting.')
                else:
                    template_ctx = {
                        'model_description': self.env['ir.model']._get('hr.appraisal').display_name,
                        'message': self.env['mail.message'].sudo().new(dict(body=mail_values['body_html'], record_name=_("Appraisal Request"))),
                        'company': self.env.company,
                    }
                    body = template._render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                    mail_values['body_html'] = self.env['mail.render.mixin']._replace_local_links(body)
                self.env['mail.mail'].sudo().create(mail_values)

                if employee.user_id:
                    appraisal.activity_schedule(
                        'mail.mail_activity_data_todo', appraisal.date_close,
                        summary=_('Appraisal Form to Fill'),
                        note=_('Fill appraisal for <a href="#" data-oe-model="%s" data-oe-id="%s">%s</a>') % (
                            appraisal.employee_id._name, appraisal.employee_id.id, appraisal.employee_id.display_name),
                        user_id=employee.user_id.id)

    def action_cancel(self):
        self.state = 'cancel'

    def _update_previous_appraisal(self):
        for employee in set(self.mapped('employee_id')):
            appraisals = employee.appraisal_ids.filtered(lambda a: a.state != 'cancel').sorted('date_close')
            appraisals_index = {v.id: i for i, v in enumerate(appraisals)}

            for appraisal in appraisals:
                index = appraisals_index[appraisal.id] - 1
                if index >= 0 and index < len(appraisals):
                    appraisal.previous_appraisal_id = appraisals[index]
                else:
                    appraisal.previous_appraisal_id = False

    def _update_next_appraisal_date(self):
        for employee in set(self.mapped('employee_id')):
            appraisals = employee.appraisal_ids.filtered(lambda a: a.state not in ['done', 'cancel']).sorted('date_close')
            employee.sudo().write({'next_appraisal_date': appraisals[0].date_close if appraisals else False})
            if employee.last_appraisal_id.state != 'done':
                employee.sudo().write({
                    'last_appraisal_id': appraisals[0].id if appraisals else False,
                    'last_appraisal_date': appraisals[0].date_close if appraisals else False
                })

    @api.model
    def create(self, vals):
        result = super(HrAppraisal, self).create(vals)
        result.sudo()._update_previous_appraisal()
        if vals.get('state') and vals['state'] == 'pending':
            self.send_appraisal()
        result.sudo()._update_next_appraisal_date()
        result.subscribe_employees()
        return result

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'pending':
            self.send_appraisal()
        if 'state' in vals and vals['state'] == 'done':
            vals['employee_feedback_published'] = True
            vals['manager_feedback_published'] = True
            current_date = datetime.date.today()
            self.activity_feedback(['mail.mail_activity_data_meeting', 'mail.mail_activity_data_todo'])
            for appraisal in self:
                appraisal.employee_id.sudo().write({
                    'last_appraisal_id': appraisal.id,
                    'last_appraisal_date': current_date,
                    'next_appraisal_date': False})
            vals['date_close'] = current_date
            self._appraisal_plan_post()
        if 'state' in vals and vals['state'] == 'cancel':
            self.meeting_ids.unlink()
            self.activity_unlink(['mail.mail_activity_data_meeting', 'mail.mail_activity_data_todo'])
            current_date = datetime.date.today()
            vals['date_close'] = current_date
        previous_managers = {}
        if 'manager_ids' in vals:
            previous_managers = {x: y for x, y in self.mapped(lambda a: (a.id, a.manager_ids))}
        result = super(HrAppraisal, self).write(vals)
        if 'employee_id' in vals or 'date_close' in vals:
            self.sudo()._update_previous_appraisal()
        if vals.get('date_close'):
            self.sudo()._update_next_appraisal_date()
        if 'manager_ids' in vals:
            self._sync_meeting_attendees(previous_managers)
        return result

    def _appraisal_plan_post(self):
        gigabot = self.env.ref('base.partner_root')
        days = int(self.env['ir.config_parameter'].sudo().get_param('hr_appraisal.appraisal_create_in_advance_days', 8))
        for appraisal in self:
            if not appraisal.appraisal_plan_posted and appraisal.company_id.appraisal_plan and not appraisal.employee_id.next_appraisal_date:
                month = appraisal.company_id.duration_first_appraisal if appraisal.employee_id.sudo().appraisal_count == 1 else appraisal.company_id.duration_next_appraisal
                date = (datetime.date.today() + relativedelta(months=month, days=-days))
                formated_date = format_date(self.env, date, date_format="MMM d y")
                body = _('Thanks to your Appraisal Plan, without any new manual Appraisal, the new Appraisal will be automatically created on %s.', formated_date)
                appraisal.message_post(body=body, author_id=gigabot.id)
                appraisal.appraisal_plan_posted = True

    def _sync_meeting_attendees(self, manager_ids):
        for appraisal in self.filtered('meeting_ids'):
            previous_managers = manager_ids.get(appraisal.id, self.env['hr.employee'])
            to_add = self.manager_ids - previous_managers
            to_del = previous_managers - self.manager_ids
            if to_add or to_del:
                appraisal.meeting_ids.write({
                    'partner_ids': [
                        *[(3, x) for x in to_del.mapped('related_partner_id').ids],
                        *[(4, x) for x in to_add.mapped('related_partner_id').ids],
                    ]
                })

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancel(self):
        if any(appraisal.state not in ['new', 'cancel'] for appraisal in self):
            raise UserError(_("You cannot delete appraisal which is not in draft or canceled state"))

    def read(self, fields=None, load='_classic_read'):
        check_feedback = set(fields) & {'manager_feedback', 'employee_feedback'}
        check_notes = set(fields) & {'note', 'assessment_note'}
        if check_feedback:
            fields = fields + ['can_see_employee_publish', 'can_see_manager_publish', 'employee_feedback_published', 'manager_feedback_published']
        if check_notes:
            fields = fields + ['employee_id']
        records = super().read(fields, load)
        if check_feedback:
            for appraisal in records:
                if not appraisal['can_see_employee_publish'] and not appraisal['employee_feedback_published']:
                    appraisal['employee_feedback'] = _('Unpublished')
                if not appraisal['can_see_manager_publish'] and not appraisal['manager_feedback_published']:
                    appraisal['manager_feedback'] = _('Unpublished')
        if check_notes:
            for appraisal in records:
                if appraisal['employee_id'][0] == self.env.user.employee_id.id:
                    appraisal['note'] = _('Note')
                    appraisal['assessment_note'] = (1, _('Assessment'))
        return records

    def action_calendar_event(self):
        self.ensure_one()
        partners = self.manager_ids.mapped('related_partner_id') | self.employee_id.related_partner_id | self.env.user.partner_id
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context'] = {
            'default_partner_ids': partners.ids,
            'default_res_model': 'hr.appraisal',
            'default_res_id': self.id,
            'default_name': _('Appraisal of %s', self.employee_id.name),
        }
        return action

    def action_confirm(self):
        self.write({'state': 'pending'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_back(self):
        self.action_confirm()

    def action_open_last_appraisal(self):
        self.ensure_one()
        return {
            'view_mode': 'form',
            'res_model': 'hr.appraisal',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.previous_appraisal_id.id,
        }

    def action_open_goals(self):
        self.ensure_one()
        return {
            'name': _('%s Goals') % self.employee_id.name,
            'view_mode': 'kanban,tree,form',
            'res_model': 'hr.appraisal.goal',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }

    def action_send_appraisal_request(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'request.appraisal',
            'target': 'new',
            'name': _('Appraisal Request'),
            'context': {'default_appraisal_id': self.id},
        }
