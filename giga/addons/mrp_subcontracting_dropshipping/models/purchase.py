# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, _
from giga.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _get_destination_location(self):
        self.ensure_one()
        if not self.dest_address_id:
            return super()._get_destination_location()

        if self.mrp_production_count:
            mrp_production_ids = self._get_mrp_productions()
            if self.dest_address_id in mrp_production_ids.bom_id.subcontractor_ids:
                return self.dest_address_id.property_stock_subcontractor.id
        elif self.sale_order_count:
            return super()._get_destination_location()

        in_bom_products = False
        not_in_bom_products = False
        for order_line in self.order_line:
            if any(bom_line.bom_id.type == 'subcontract' and self.dest_address_id in bom_line.bom_id.subcontractor_ids for bom_line in order_line.product_id.bom_line_ids.filtered(lambda line: line.company_id == self.company_id)):
                in_bom_products = True
            else:
                not_in_bom_products = True
        if in_bom_products and not_in_bom_products:
            raise UserError(_("It appears some components in this RFQ are not meant for subcontracting. Please create a separate order for these."))
        elif in_bom_products:
            return self.dest_address_id.property_stock_subcontractor.id
        return super()._get_destination_location()
