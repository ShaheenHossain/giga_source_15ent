# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models, api, _
from giga.exceptions import UserError


class EventMailScheduler(models.Model):
    _inherit = 'event.mail'

    @api.model
    def _selection_template_model(self):
        return super(EventMailScheduler, self)._selection_template_model() + [('social.post.template', 'Social')]

    notification_type = fields.Selection(selection_add=[('social_post', 'Social Post')], ondelete={'social_post': 'set default'})

    @api.depends('notification_type')
    def _compute_template_model_id(self):
        social_model = self.env['ir.model']._get('social.post.template')
        social_mails = self.filtered(lambda mail: mail.notification_type == 'social_post')
        social_mails.template_model_id = social_model
        super(EventMailScheduler, self - social_mails)._compute_template_model_id()

    @api.constrains('template_ref', 'interval_type')
    def _check_interval_type(self):
        """Cannot select "after_sub" if the notification type is "social_post"."""
        for mail in self:
            if mail.template_ref and mail.template_ref._name == 'social.post.template' and mail.interval_type == 'after_sub':
                raise UserError(_('As social posts have no recipients, they cannot be triggered by registrations.'))

    def execute(self):
        social_post_mails = self.filtered(
            lambda mail:
                mail.template_ref
                and mail.notification_type == 'social_post'
                and not mail.mail_done
        )

        social_posts_values = [
            scheduler.template_ref._prepare_social_post_values()
            for scheduler in social_post_mails
            if scheduler.template_ref.account_ids
        ]

        self.env['social.post'].sudo().create(social_posts_values)._action_post()

        for social_post_mail in social_post_mails:
            social_post_mails.update({
                'mail_done': True,
                'mail_count_done': len(social_post_mail.template_ref.account_ids),
            })

        return super(EventMailScheduler, self - social_post_mails).execute()
