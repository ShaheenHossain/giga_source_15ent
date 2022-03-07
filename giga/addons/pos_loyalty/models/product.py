# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, _
from giga.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def write(self, vals):
        if 'active' in vals and not vals['active']:
            product_in_reward = self.env['loyalty.reward'].sudo().search(['|', ('gift_product_id', 'in', self.ids),
                                                                 ('discount_product_id', 'in', self.ids)], limit=1)
            if product_in_reward:
                raise ValidationError(_("The product cannot be archived because it's used in a point of sales loyalty program."))
        super().write(vals)
