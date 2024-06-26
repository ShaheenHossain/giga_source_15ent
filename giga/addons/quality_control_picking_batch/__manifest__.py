# -*- encoding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quality - Batch Transfer',
    'version': '1.0',
    'category': 'Manufacturing/Quality',
    'summary': 'Support of quality control into batch transfers',
    'depends': [
        'quality_control',
        'stock_picking_batch',
    ],
    'data': [
        'views/stock_picking_batch_views.xml',
    ],
    'auto_install': True,
    'application': False,
    'installable': True,
    'license': 'OEEL-1',
}
