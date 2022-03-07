# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from .taxcloud_request import TaxCloudRequest
from giga import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_TaxCloudRequest(self, api_id, api_key):
        return TaxCloudRequest(api_id, api_key)

    def _get_reward_values_free_shipping(self, program):
        res = super(SaleOrder, self)._get_reward_values_free_shipping(program)
        res.update(coupon_program_id=program.id)
        return res
