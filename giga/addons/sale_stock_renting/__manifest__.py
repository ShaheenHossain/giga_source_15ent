# -*- coding: utf-8 -*-
{
    'name': "Rental Stock Management",

    'summary': """
Allows use of stock application to manage rentals inventory
        """,

    'description': """

    """,

    'author': "Giga Source ERP",
    'website': "https://www.gigasource.de",

    'category': 'Sales/Sales',
    'version': '1.0',

    'depends': ['sale_renting', 'sale_stock'],

    'data': [
        'data/rental_stock_data.xml',
        'wizard/rental_configurator_views.xml',
        'wizard/rental_processing_views.xml',
        'report/rental_schedule_views.xml',
        'report/rental_report_views.xml',
        'report/rental_order_report_templates.xml',
        'views/res_config_settings_views.xml',
        'views/sale_views.xml',
        'views/product_views.xml',
    ],
    'demo': [
        'data/rental_stock_demo.xml',
    ],
    'auto_install': True,
    'post_init_hook': '_ensure_rental_stock_moves_consistency',
    'assets': {
        'web.assets_backend': [
            'sale_stock_renting/static/src/js/**/*',
        ],
        'web.assets_qweb': [
            'sale_stock_renting/static/src/xml/**/*',
        ],
    },
    'license': 'OEEL-1',
}
