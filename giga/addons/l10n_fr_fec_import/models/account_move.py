# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fec_matching_number = fields.Char(help="Matching code that is used in FEC import for reconciliation")
