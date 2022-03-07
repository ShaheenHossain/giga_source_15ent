# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class EventMenu(models.Model):
    _inherit = "website.event.menu"

    menu_type = fields.Selection(
        selection_add=[('booth', 'Event Booth Menus')], ondelete={'booth': 'cascade'})
