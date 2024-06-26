# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
{
    'name': "Account Taxcloud - Sale (coupon) - Delivery",
    'summary': """Manage discounts in taxclouds computations with delivery.""",
    'description': """
    Manage discounts with deliveries in taxclouds computations.
    This module follows the same logic as "Account Taxcloud - Sale (coupon)".
    More information can be found there on how discount computations are made for TaxCloud.

    There is an added option for discount (free shipping) on deliveries.
    With Sale coupon delivery, the discount computation does not apply on delivery lines.
    """,
    'category': 'Accounting',
    'depends': ['sale_coupon_taxcloud', 'sale_coupon_delivery'],
    'auto_install': True,
    'license': 'OEEL-1',
}
