# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import http
from giga.http import request
from giga.addons.http_routing.models.ir_http import slug
from giga.addons.website_event.controllers.main import WebsiteEventController
from giga.tools import is_html_empty


class WebsiteEventTwitterWallController(WebsiteEventController):
    @http.route([
        '/event/<model("event.event"):event>/social',
        '/event/<model("event.event"):event>/social/page/<int:page>'
    ], type='http', auth="public", website=True, sitemap=False)
    def event_social(self, event, page=1):
        tweets_count = 15
        wall = event.twitter_wall_id
        pager = request.website.pager(url='/event/%s/social' % slug(event), total=wall.total_tweets, page=page, step=tweets_count, scope=tweets_count)
        tweets = request.env['website.twitter.tweet'].search([('wall_ids', 'in', wall.id)], limit=tweets_count, offset=pager['offset'], order='id desc')
        return request.render('website_event_twitter_wall.event_twitter_wall_view', {
            'main_object': event,
            'event': event,
            'wall': wall,
            'tweets': tweets,
            'pager': pager,
            'is_html_empty': is_html_empty,
        })
