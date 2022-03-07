# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, _
from giga.addons.http_routing.models.ir_http import url_for


class Website(models.Model):
    _inherit = "website"

    def get_suggested_controllers(self):
        suggested_controllers = super(Website, self).get_suggested_controllers()
        suggested_controllers.append((_('Helpdesk Customer Satisfaction'), url_for('/helpdesk/rating'), 'helpdesk'))
        return suggested_controllers

    def configurator_get_footer_links(self):
        links = super().configurator_get_footer_links()
        links.append({'text': _("Help"), 'href': '/help'})
        return links