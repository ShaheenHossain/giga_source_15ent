# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga.addons.event_booth.tests.common import TestEventBoothCommon
from giga.addons.event_sale.tests.common import TestEventSaleCommon


class TestEventBoothSaleCommon(TestEventBoothCommon, TestEventSaleCommon):

    @classmethod
    def setUpClass(cls):
        super(TestEventBoothSaleCommon, cls).setUpClass()

        cls.event_booth_product = cls.env['product.product'].create({
            'name': 'Test Booth Product',
            'description_sale': 'Mighty Booth Description',
            'list_price': 20,
            'standard_price': 60.0,
            'detailed_type': 'event_booth',
        })
        (cls.event_booth_category_1 + cls.event_booth_category_2).write({
            'product_id': cls.event_booth_product.id,
        })
