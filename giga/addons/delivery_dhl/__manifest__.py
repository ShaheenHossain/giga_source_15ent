# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
{
    'name': "DHL Express Shipping",
    'description': "Send your shippings through DHL and track them online",
    'category': 'Inventory/Delivery',
    'sequence': 285,
    'version': '1.0',
    'application': True,
    'depends': ['delivery', 'mail'],
    'data': [
        'data/delivery_dhl_data.xml',
        'views/delivery_dhl_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'license': 'OEEL-1',
}
