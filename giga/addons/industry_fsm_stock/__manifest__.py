# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Field Service Stock',
    'category': 'Hidden',
    'summary': 'Validate stock moves for product added on sales orders through Field Service Management App',
    'description': """
Validate stock moves for Field Service
======================================
""",
    'depends': ['industry_fsm_sale', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_product_views.xml',
        'wizard/fsm_stock_tracking_views.xml',
    ],
    'auto_install': True,
    'license': 'OEEL-1',
}
