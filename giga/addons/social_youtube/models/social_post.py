# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import _, api, fields, models
from giga.exceptions import UserError
from giga.osv import expression


class SocialPostYoutube(models.Model):
    _inherit = 'social.post'

    youtube_video = fields.Char('YouTube Video',
        help="Simply holds the filename of the video as the video itself is uploaded directly to YouTube")
    youtube_video_id = fields.Char('YouTube Video Id',
        help="Contains the ID of the video as returned by the YouTube API")
    youtube_video_category_id = fields.Char('YouTube Category Id',
        help="Contains the ID of the video category as returned by the YouTube API")
    youtube_access_token = fields.Char('YouTube Access Token',
        compute='_compute_youtube_access_token')
    youtube_title = fields.Char('YouTube Video Title')
    youtube_description = fields.Text('YouTube Video Description')
    youtube_preview = fields.Html('YouTube Preview', compute='_compute_youtube_preview')
    youtube_accounts_count = fields.Integer('Selected YouTube Accounts',
        compute='_compute_youtube_accounts_count')
    youtube_accounts_other_count = fields.Integer('Selected Other Accounts',
        compute='_compute_youtube_accounts_count')

    @api.constrains('message')
    def _check_message_not_empty(self):
        """ When posting only on YouTube, the 'message' field can (and should) be empty. """
        for social_post in self:
            if 'youtube' not in social_post.media_ids.mapped('media_type'):
                super(SocialPostYoutube, self)._check_message_not_empty()
            elif not social_post.message and ['youtube'] != social_post.media_ids.mapped('media_type'):
                raise UserError(_("The 'message' field is required for post ID %s", social_post.id))

    @api.depends('youtube_video_id')
    def _compute_stream_posts_count(self):
        super(SocialPostYoutube, self)._compute_stream_posts_count()

    @api.depends('account_ids.media_type', 'account_ids.youtube_access_token')
    def _compute_youtube_access_token(self):
        for post in self:
            youtube_account = post.account_ids.filtered(lambda account: account.media_type == 'youtube')
            if len(youtube_account) == 1:
                youtube_account._refresh_youtube_token()
                post.youtube_access_token = youtube_account.youtube_access_token
            else:
                post.youtube_access_token = False

    @api.depends('youtube_title', 'youtube_description', 'youtube_video_id', 'scheduled_date')
    def _compute_youtube_preview(self):
        for post in self:
            post.youtube_preview = self.env.ref('social_youtube.youtube_preview')._render({
                'youtube_title': post.youtube_title or _('Video'),
                'youtube_description': post.youtube_description,
                'youtube_video_id': post.youtube_video_id,
                'published_date': post.scheduled_date if post.scheduled_date else fields.Datetime.now(),
            })

    @api.depends('account_ids.media_type')
    def _compute_youtube_accounts_count(self):
        for post in self:
            post.youtube_accounts_count = len(post.account_ids.filtered(
                lambda account: account.media_type == 'youtube'))
            post.youtube_accounts_other_count = len(post.account_ids) - post.youtube_accounts_count

    def _check_post_access(self):
        super(SocialPostYoutube, self)._check_post_access()

        for social_post in self:
            if social_post.youtube_accounts_count > 1:
                raise UserError(_("Please select a single YouTube account at a time."))
            if not social_post.youtube_video_id and 'youtube' in social_post.media_ids.mapped('media_type'):
                raise UserError(_("You have to upload a video when posting on YouTube."))

    def _get_stream_post_domain(self):
        domain = super(SocialPostYoutube, self)._get_stream_post_domain()
        youtube_video_ids = [youtube_video_id for youtube_video_id in self.mapped('youtube_video_id') if youtube_video_id]
        if youtube_video_ids:
            return expression.OR([domain, [('youtube_video_id', 'in', youtube_video_ids)]])
        else:
            return domain

    @api.model
    def _prepare_post_content(self, message, media_type, **kw):
        message = super(SocialPostYoutube, self)._prepare_post_content(message, media_type, **kw)
        if media_type != 'youtube' and kw.get('youtube_video_id'):
            message += f'\n\nhttps://youtube.com/watch?v={kw.get("youtube_video_id")}'
        return message

    @api.model
    def _get_post_message_modifying_fields(self):
        return super(SocialPostYoutube, self)._get_post_message_modifying_fields() + ['youtube_video_id']
