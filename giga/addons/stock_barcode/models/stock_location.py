# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, api


class Location(models.Model):
    _inherit = 'stock.location'
    _barcode_field = 'barcode'

    @api.model
    def _get_fields_stock_barcode(self):
        return ['display_name', 'barcode', 'parent_path']
