# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models


class SocialPostTemplate(models.Model):
    _inherit = 'social.post.template'

    facebook_preview = fields.Html('Facebook Preview', compute='_compute_facebook_preview')
    display_facebook_preview = fields.Boolean('Display Facebook Preview', compute='_compute_display_facebook_preview')

    @api.depends('message', 'account_ids.media_id.media_type')
    def _compute_display_facebook_preview(self):
        for post in self:
            post.display_facebook_preview = post.message and ('facebook' in post.account_ids.media_id.mapped('media_type'))

    @api.depends(lambda self: ['message', 'image_ids'] + self._get_post_message_modifying_fields())
    def _compute_facebook_preview(self):
        for post in self:
            post.facebook_preview = self.env.ref('social_facebook.facebook_preview')._render({
                'message': post._prepare_post_content(
                    post.message,
                    'facebook',
                    **{field: post[field] for field in post._get_post_message_modifying_fields()}),
                'published_date': fields.Datetime.now(),
                'images': [
                    image.with_context(bin_size=False).datas
                    for image in post.image_ids.sorted(lambda image: image._origin.id or image.id, reverse=True)
                ]
            })
