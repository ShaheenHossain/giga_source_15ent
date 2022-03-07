# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import _, models
from giga.exceptions import UserError


class ReportProductLabel(models.AbstractModel):
    _name = 'report.stock.label_product_product_view'
    _description = 'Product Label Report'

    def _get_report_values(self, docids, data):
        if data.get('active_model') == 'product.template':
            data['quantity'] = {self.env['product.template'].browse(int(p)): q for p, q in data.get('quantity_by_product').items()}
        elif data.get('active_model') == 'product.product':
            data['quantity'] = {self.env['product.product'].browse(int(p)): q for p, q in data.get('quantity_by_product').items()}
        else:
            raise UserError(_('Product model not defined, Please contact your administrator.'))

        return data
