# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import requests
from datetime import timedelta
from werkzeug.urls import url_join

from giga import api, fields, models


class SocialAccountYoutube(models.Model):
    _inherit = 'social.account'

    youtube_channel_id = fields.Char('Youtube Channel ID', readonly=True,
        help="YouTube Channel ID provided by the YouTube API, this should never be set manually.")
    youtube_access_token = fields.Char('Google Access Token', readonly=True,
        help="Access token provided by the YouTube API, this should never be set manually.")
    youtube_refresh_token = fields.Char('Google Refresh Token', readonly=True,
        help="Refresh token provided by the YouTube API, this should never be set manually.")
    youtube_token_expiration_date = fields.Datetime('Token expiration date', readonly=True,
        help="Expiration date of the Access Token provided by the Youtube API, this should never be set manually.")
    youtube_upload_playlist_id = fields.Char('YouTube Upload Playlist ID', readonly=True,
         help="'Uploads' Playlist ID provided by the YouTube API, this should never be set manually.")

    def _compute_stats_link(self):
        """ External link to this Youtube Page's Analytics. """
        youtube_accounts = self._filter_by_media_types(['youtube'])
        super(SocialAccountYoutube, (self - youtube_accounts))._compute_stats_link()

        for account in youtube_accounts:
            account.stats_link = "https://studio.youtube.com/channel/%s/analytics/tab-overview" % account.youtube_channel_id

    def _compute_statistics(self):
        youtube_accounts = self._filter_by_media_types(['youtube'])
        super(SocialAccountYoutube, (self - youtube_accounts))._compute_statistics()
        endpoint_url = url_join(self.env['social.media']._YOUTUBE_ENDPOINT, "youtube/v3/channels")

        for account in youtube_accounts:
            account._refresh_youtube_token()

            stats_response = requests.get(endpoint_url,
                params={
                    'access_token': account.youtube_access_token,
                    'id': account.youtube_channel_id,
                    'part': 'statistics',
                },
                timeout=5
            ).json()

            if stats_response.get('error'):
                account.write({'is_media_disconnected': True})
            else:
                stats = stats_response.get('items', [{}])[0].get('statistics', {})
                account.write({
                    'audience': stats.get('subscriberCount', 0),
                    'engagement': stats.get('viewCount', 0),
                    'stories': stats.get('commentCount', 0),
                })

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SocialAccountYoutube, self).create(vals_list)
        res.filtered(lambda account: account.media_type == 'youtube')._create_default_stream_youtube()
        return res

    def _create_default_stream_youtube(self):
        """ This will create a stream to show the account video for each created account.
        It helps with onboarding to have your videos show up on the 'Feed' view as
        soon as you have configured your accounts."""

        page_posts_stream_type = self.env.ref('social_youtube.stream_type_youtube_channel_videos')
        self.env['social.stream'].create([{
            'media_id': account.media_id.id,
            'stream_type_id': page_posts_stream_type.id,
            'account_id': account.id}
            for account in self
        ])

    def _refresh_youtube_token(self):
        """ YouTube works with both an access_token, used to authenticate API requests, and a
        refresh_token used to grant a new refresh_token when it expires.
        Access tokens have a very short life span (a few hours) so we have to make sure we're
        refreshing the token often, ideally checking before every single API call.
        This method handles both:
        - Database is configured to use 'Own YouTube account'
          That will negotiate the new access_token using the Google API directly
        - Using our IAP proxy (for databases with valid enterprise subscriptions)
          That will receive the new access_token from our IAP proxy. """

        youtube_oauth_client_id = self.env['ir.config_parameter'].sudo().get_param('social.youtube_oauth_client_id')
        youtube_oauth_client_secret = self.env['ir.config_parameter'].sudo().get_param('social.youtube_oauth_client_secret')

        for account in self:
            if not account.youtube_token_expiration_date or account.youtube_token_expiration_date > fields.Datetime.now():
                continue

            if youtube_oauth_client_id and youtube_oauth_client_secret:
                token_refresh_response = requests.post('https://oauth2.googleapis.com/token',
                    data={
                        'client_id': youtube_oauth_client_id,
                        'client_secret': youtube_oauth_client_secret,
                        'grant_type': 'refresh_token',
                        'refresh_token': account.youtube_refresh_token
                    },
                    timeout=5
                ).json()
            else:
                social_iap_endpoint = self.env['ir.config_parameter'].sudo().get_param(
                    'social.social_iap_endpoint',
                    self.env['social.media']._DEFAULT_SOCIAL_IAP_ENDPOINT
                )

                token_refresh_response = requests.get(
                    url_join(social_iap_endpoint, 'api/social/youtube/1/refresh_token'),
                    params={
                        'db_uuid': self.env['ir.config_parameter'].sudo().get_param('database.uuid'),
                        'refresh_token': account.youtube_refresh_token
                    },
                    timeout=5
                ).json()

            if token_refresh_response.get('error'):
                account.sudo().write({'is_media_disconnected': True})
            else:
                account.sudo().write({
                    'youtube_access_token': token_refresh_response['access_token'],
                    'youtube_token_expiration_date': fields.Datetime.now() + timedelta(
                        seconds=token_refresh_response.get('expires_in', 0)),
                    'is_media_disconnected': False
                })
