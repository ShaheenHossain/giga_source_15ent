# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    transfer_model_id = fields.Many2one('account.transfer.model', string="Originating Model")
