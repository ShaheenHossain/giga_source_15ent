# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Planning',
    'category': 'Hidden',
    'description': """
        This module allows you to schedule your Sales Order based on the product configuration.

        For products on which the "Plan Services" option is enabled, you will have the opportunity
        to automatically plan the shifts for employees whom are able to take the shift
        (i.e. employees who have the same role as the one configured on the product).

        Plan shifts and keep an eye on the hours consumed on your plannable products.
    """,
    'depends': ['sale_management', 'planning'],
    'data': [
        'security/ir.model.access.csv',
        'security/sale_planning_security.xml',
        'views/planning_role_views.xml',
        'views/planning_slot_views.xml',
        'views/planning_templates.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [
        'data/product_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_planning/static/src/js/backend/**/*',
        ],
        'web.assets_frontend': [
            'sale_planning/static/src/js/frontend/**/*',
        ],
        'web.assets_qweb': [
            'sale_planning/static/src/xml/**/*',
        ],
    },
    'auto_install': True,
    'license': 'OEEL-1',
}
