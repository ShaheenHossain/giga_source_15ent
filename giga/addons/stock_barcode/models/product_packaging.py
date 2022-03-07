# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, api


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'
    _barcode_field = 'barcode'

    @api.model
    def _get_fields_stock_barcode(self):
        return ['barcode', 'product_id', 'qty']
