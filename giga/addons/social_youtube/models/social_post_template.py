# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models
from giga.osv import expression


class SocialPostTemplateYoutube(models.Model):
    _inherit = 'social.post.template'

    def _get_default_accounts_domain(self):
        """ As YouTube requires 'extra work' (video upload, ...), we don't want it selected by default.

        It will also not be available for the social post template.
        """
        youtube_media = self.env.ref('social_youtube.social_media_youtube')
        return expression.AND([
            super(SocialPostTemplateYoutube, self)._get_default_accounts_domain(),
            [('media_id', '!=', youtube_media.id)]
        ])
