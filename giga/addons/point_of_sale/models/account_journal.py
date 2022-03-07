# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2004-2008 PC Solutions (<http://pcsol.be>). All Rights Reserved
from giga import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    pos_payment_method_ids = fields.One2many('pos.payment.method', 'journal_id', string='Point of Sale Payment Methods')
