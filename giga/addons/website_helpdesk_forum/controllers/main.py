# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga.http import request
from giga.addons.website_helpdesk.controllers import main


class WebsiteHelpdesk(main.WebsiteHelpdesk):

    def get_helpdesk_team_data(self, team, search=None):
        result = super(WebsiteHelpdesk, self).get_helpdesk_team_data(team, search)
        result['forum'] = team.forum_id
        domain = []
        if search:
            domain += [('name', 'ilike', search)]
        if team.forum_id:
            domain += [('forum_id', '=', result['forum'].id), ('parent_id', '=', False)]
            questions = request.env['forum.post'].search(domain)
            result['questions'] = questions[:10]
            result['questions_limit'] = len(questions)
            result['search'] = search
        return result
