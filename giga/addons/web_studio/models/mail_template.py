# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models


class MailTemplate(models.Model):
    _name = 'mail.template'
    _description = 'Email Templates'
    _inherit = ['studio.mixin', 'mail.template']
