# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
{
    'name': "UPS Shipping",
    'description': "Send your shippings through UPS and track them online",
    'category': 'Inventory/Delivery',
    'sequence': 275,
    'version': '1.0',
    'application': True,
    'depends': ['delivery', 'mail'],
    'data': [
        'data/delivery_ups_data.xml',
        'views/delivery_ups_view.xml',
        'views/res_config_settings_views.xml',
        'views/sale_views.xml',
        'views/res_partner_views.xml',
    ],
    'license': 'OEEL-1',
}
