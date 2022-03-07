# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class MailMail(models.Model):
    _inherit = 'mail.mail'

    fetchmail_server_id = fields.Many2one('fetchmail.server', "Inbound Mail Server", readonly=True, index=True)
