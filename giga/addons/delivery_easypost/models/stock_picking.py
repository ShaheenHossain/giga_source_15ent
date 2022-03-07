# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ep_order_ref = fields.Char("Easypost Order Reference", copy=False)
