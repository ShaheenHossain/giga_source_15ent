# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
{
    'name': 'UNSPSC product codes',
    'version': '0.2',
    'category': 'Hidden',
    'summary': 'UNSPSC product codes',
    'description': """
        Countries like Colombia, Peru and Mexico need to be able to use the
        UNSPSC code for their products and uoms.
    """,
    'depends': ['account'],
    'data': ['views/product_views.xml',
             'security/ir.model.access.csv'],
    "post_init_hook": "post_init_hook",
    'installable': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
    'license': 'OEEL-1',
}
