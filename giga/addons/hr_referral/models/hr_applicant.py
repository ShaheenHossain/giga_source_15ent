# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import json
from werkzeug.urls import url_encode

from giga import api, fields, models, _
from giga.exceptions import AccessError, UserError
from giga.osv import expression


class Applicant(models.Model):
    _inherit = ["hr.applicant"]

    ref_user_id = fields.Many2one('res.users', string='Referred By User', tracking=True,
        compute='_compute_ref_user_id', inverse='_inverse_ref_user_id', store=True, copy=False)
    referral_points_ids = fields.One2many('hr.referral.points', 'applicant_id', copy=False)
    earned_points = fields.Integer(compute='_compute_earned_points')
    referral_state = fields.Selection([
        ('progress', 'In Progress'),
        ('hired', 'Hired'),
        ('closed', 'Not Hired')], required=True, default='progress')
    shared_item_infos = fields.Text(compute="_compute_shared_item_infos")
    max_points = fields.Integer(related="job_id.max_points")
    friend_id = fields.Many2one('hr.referral.friend', copy=False)
    last_valuable_stage_id = fields.Many2one('hr.recruitment.stage', "Last Valuable Stage")

    @api.depends('source_id')
    def _compute_ref_user_id(self):
        for applicant in self:
            if applicant.source_id:
                applicant.ref_user_id = self.env['res.users'].search([('utm_source_id', '=', applicant.source_id.id)], limit=1)
            else:
                applicant.ref_user_id = False

    def _inverse_ref_user_id(self):
        for applicant in self:
            applicant.source_id = applicant.ref_user_id.utm_source_id

    def _check_referral_fields_access(self, fields):
        referral_fields = {'name', 'partner_name', 'job_id', 'referral_points_ids', 'earned_points', 'max_points',
                           'shared_item_infos', 'referral_state', 'user_id', 'friend_id', '__last_update'}
        if not self.user_has_groups('hr_recruitment.group_hr_recruitment_user'):
            if set(fields or []) - referral_fields:
                raise AccessError(_('You are not allowed to access applicant records.'))

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        self._check_referral_fields_access(fields)
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)

    def read(self, fields, load='_classic_read'):
        self._check_referral_fields_access(fields)
        return super().read(fields, load)

    @api.depends('referral_points_ids')
    def _compute_shared_item_infos(self):
        for applicant in self:
            stages = self.env['hr.recruitment.stage'].search([('use_in_referral', '=', True), '|', ('job_ids', '=', False), ('job_ids', '=', applicant.job_id.id)])
            infos = [{
                'name': stage.name,
                'points': stage.points,
                'done': bool(len(applicant.referral_points_ids.filtered(lambda point: point.stage_id == stage and point.points > 0))
                    > len(applicant.referral_points_ids.filtered(lambda point: point.stage_id == stage and point.points < 0))),
                'seq': stage.sequence,
            } for stage in stages]
            applicant.shared_item_infos = json.dumps(infos)

    def _compute_earned_points(self):
        for applicant in self:
            applicant.earned_points = sum(applicant.referral_points_ids.mapped('points'))

    def write(self, vals):
        res = super(Applicant, self).write(vals)
        if 'ref_user_id' in vals or 'stage_id' in vals or 'date_closed' in vals:
            for applicant in self.filtered(lambda a: a.ref_user_id):
                if 'ref_user_id' in vals:
                    applicant.referral_points_ids.unlink()
                applicant.sudo()._update_points(applicant.stage_id.id, vals.get('last_stage_id', False))
                if 'stage_id' in vals and vals['stage_id']:
                    if self.env['hr.recruitment.stage'].browse(vals['stage_id']).use_in_referral:
                        applicant.last_valuable_stage_id = vals['stage_id']
                if 'date_closed' in vals:
                    if not vals['date_closed'] and not applicant.stage_id.hired_stage:
                        applicant.referral_state = 'progress'
        return res

    @api.model
    def create(self, vals):
        res = super(Applicant, self).create(vals)
        if res.ref_user_id and res.stage_id:
            res.sudo()._update_points(res.stage_id.id, False)
            if res.stage_id.use_in_referral:
                res.last_valuable_stage_id = res.stage_id
        return res

    def archive_applicant(self):
        self.write({'referral_state': 'closed'})
        return super(Applicant, self).archive_applicant()

    def _send_notification(self, body):
        if self.partner_name:
            subject = _('Referral: %s (%s)') % (self.partner_name, self.name)
        else:
            subject = _('Referral: %s') % (self.name)
        url = url_encode({'action': 'hr_referral.action_hr_applicant_employee_referral', 'active_model': self._name})
        action_url = '/web#' + url
        body = ("<a class='o_document_link' href=%s>%s</a><br>%s") % (action_url, subject, body)
        gigabot = self.env.ref('base.partner_root')
        self.env['mail.thread'].sudo().message_notify(
            subject=subject,
            body=body,
            author_id=gigabot.id,
            partner_ids=[self.ref_user_id.partner_id.id],
            email_layout_xmlid='mail.mail_notification_light',
        )

    def _update_points(self, new_state_id, old_state_id):
        if not self.company_id:
            raise UserError(_("Applicant must have a company."))
        new_state = self.env['hr.recruitment.stage'].browse(new_state_id)
        if not new_state.use_in_referral:
            return
        old_state = self.env['hr.recruitment.stage'].browse(old_state_id)
        if old_state and old_state.use_in_referral:
            old_state_sequence = old_state.sequence
        elif old_state:
            old_state_sequence = self.last_valuable_stage_id.sequence or -1
        else:
            old_state_sequence = -1
        point_stage = []

        # Decrease stage sequence
        if new_state.sequence < old_state_sequence:
            stages_to_remove = self.env['hr.referral.points'].read_group(
                [
                    ('applicant_id', '=', self.id),
                    ('stage_id.sequence', '<=', old_state_sequence),
                    ('stage_id.sequence', '>', new_state.sequence)
                ], ['points'], ['stage_id'])
            for stage in stages_to_remove:
                point_stage.append({
                    'applicant_id': self.id,
                    'stage_id': stage['stage_id'][0],
                    'points': - stage['points'],
                    'ref_user_id': self.ref_user_id.id,
                    'company_id': self.company_id.id
                })
            if not self.date_closed and not new_state.hired_stage:
                self.referral_state = 'progress'

        # Increase stage sequence
        elif new_state.sequence > old_state_sequence:
            stages_to_add = self.env['hr.recruitment.stage'].search([
                ('use_in_referral', '=', True),
                ('sequence', '>', old_state_sequence), ('sequence', '<=', new_state.sequence),
                '|', ('job_ids', '=', False), ('job_ids', '=', self.job_id.id)])
            gained_points = 0
            available_points = sum(self.env['hr.referral.points'].search([('ref_user_id', '=', self.ref_user_id.id), ('company_id', '=', self.company_id.id)]).mapped('points'))
            for stage in stages_to_add:
                gained_points += stage.points
                point_stage.append({
                    'applicant_id': self.id,
                    'stage_id': stage.id,
                    'points': stage.points,
                    'sequence_stage': stage.sequence,
                    'ref_user_id': self.ref_user_id.id,
                    'company_id': self.company_id.id
                })
            available_points += gained_points
            url = '/web#%s' % url_encode({'action': 'hr_referral.action_hr_referral_reward', 'active_model': 'hr.referral.reward'})
            additional_message = (gained_points > 0 and _(" You've gained %(gained)s points with this progress.<br/>"
                "It makes you a new total of %(total)s points. Visit <a href=\"%(url)s\">this link</a> to pick a gift!",
                gained=gained_points, total=available_points, url=url)) or ''
            if self.stage_id.hired_stage:
                self.referral_state = 'hired'
                self._send_notification(_('Your referrer is hired!') + additional_message)
            else:
                self._send_notification(_('Your referrer got a step further!') + additional_message)

        self.env['hr.referral.points'].create(point_stage)

    def choose_a_friend(self, friend_id):
        self.ensure_one()
        self_sudo = self.sudo()
        if not self.env.user:
            return
        if self_sudo.ref_user_id == self.env.user and not self_sudo.friend_id:
            # Use sudo, user has normaly not the right to write on applicant
            self_sudo.write({'friend_id': friend_id})

    def _get_onboarding_steps(self):
        return [{
            'text': onboarding.text,
            'image': onboarding.image
        } for onboarding in self.env['hr.referral.onboarding'].search([])]

    def _get_friends(self, applicant_names):
        return [{
            'id': friend.id,
            'friend': applicant_names.get(friend.id, ''),
            'name': applicant_names.get(friend.id, friend.name),
            'position': friend.position,
            'image': friend.image,
        } for friend in self.env['hr.referral.friend'].search([]) if friend.id in applicant_names]

    def _get_friends_head(self, applicant_names):
        return [{
            'id': friend.id,
            'friend': applicant_names.get(friend.id, ''),
            'name': friend.name,
            'image': friend.image_head,
        } for friend in self.env['hr.referral.friend'].search([])]

    @api.model
    def retrieve_referral_welcome_screen(self):
        result = {}
        user_id = self.env.user

        result['id'] = user_id.id
        if not user_id.hr_referral_onboarding_page:
            result['onboarding_screen'] = True
            result['onboarding'] = self._get_onboarding_steps()
            return result

        applicant = self.sudo().search([('ref_user_id', '=', user_id.id)])
        applicants_hired = applicant.filtered(lambda r: r.referral_state == 'hired')
        applicant_name = {applicant_hired.friend_id.id: applicant_hired.partner_name or applicant_hired.name for applicant_hired in applicants_hired}
        applicant_without_friend = applicants_hired.filtered(lambda r: not r.friend_id)

        # If there are applicant hired without friend and available friends.
        available_friend_count = self.env['hr.referral.friend'].search_count([])
        if bool(applicant_without_friend) and (len(applicants_hired) - len(applicant_without_friend) < available_friend_count):
            result['choose_new_friend'] = True
            result['new_friend_name'] = applicant_without_friend[0].partner_name or applicant_without_friend[0].name
            result['new_friend_id'] = applicant_without_friend[0].id

            result['friends'] = self._get_friends_head(applicant_name)
            return result

        result['friends'] = self._get_friends(applicant_name)

        referal_points = self.env['hr.referral.points'].search([('ref_user_id', '=', user_id.id)])
        result['point_received'] = sum(referal_points.filtered(lambda x: not x.hr_referral_reward_id).mapped('points'))
        result['point_to_spend'] = sum(referal_points.mapped('points'))

        # Employee comes for the first time on this app
        if not user_id.hr_referral_level_id:
            user_id.hr_referral_level_id = self.env['hr.referral.level'].search([], order='points asc', limit=1).id

        current_level = user_id.hr_referral_level_id
        next_level = self.env['hr.referral.level'].search([('points', '>', current_level.points)], order='points asc', limit=1)

        result['level'] = {
            'image': current_level.image,
            'name': current_level.name,
            'points': current_level.points
        }

        # Next referral levels
        result['level_percentage'] = 100
        if next_level:
            if result['point_received'] >= next_level['points']:
                result['reach_new_level'] = True
            step_level = next_level['points'] - current_level['points']
            result['level_percentage'] = round((min(result['point_received'], next_level['points']) - current_level['points']) * 100 / step_level)

        applicant = self.sudo().search([('ref_user_id', '=', user_id.id)])
        result['referral'] = {
            'all': len(applicant),
            'hired': len(applicant.filtered(lambda r: r.referral_state == 'hired')),
            'progress': len(applicant.filtered(lambda r: r.referral_state == 'progress')),
        }

        today = fields.Date.today()
        messages = self.env['hr.referral.alert'].search([
            ('active', '=', True), ('dismissed_user_ids', 'not in', self.env.user.id),
            '|', ('date_from', '<=', today), ('date_from', '=', False),
            '|', ('date_to', '>', today), ('date_to', '=', False)])

        action_name = 'hr_referral.action_hr_job_employee_referral'
        result['message'] = [{
            'id': message.id,
            'text': message.name,
            'action': action_name if message.onclick == 'all_jobs' else False,
            'url': message.url if message.onclick == 'url' else False
        } for message in messages]

        return result

    @api.model
    def upgrade_level(self):
        if not self.env.user:
            return
        user_id = self.env.user
        user_points = sum(self.env['hr.referral.points'].search([
            ('ref_user_id', '=', user_id.id),
            ('hr_referral_reward_id', '=', False)]).mapped('points'))
        next_referral_level = self.env['hr.referral.level'].search([
            ('points', '>', user_id.hr_referral_level_id.points),
            ('points', '<=', user_points)
        ], order='points asc', limit=1)
        if next_referral_level:
            user_id.write({'hr_referral_level_id': next_referral_level.id})


class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    points = fields.Integer('Points', help="Amount of points that the referent will receive when the applicant will reach this stage")
    use_in_referral = fields.Boolean('Show in Referrals', help="This option is used in app 'Referrals'. If checked, the stage is displayed in 'Referrals Dashboard' and points are given to the employee.")
