# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, _


class FollowupLine(models.Model):
    _inherit = 'account_followup.followup.line'

    send_letter = fields.Boolean('Send a Letter', help="When processing, it will send a letter by Post", default=True)
