# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Event Barcode in Mobile',
    'category': 'Marketing/Events',
    'summary': 'Event Barcode scan in Mobile',
    'version': '1.0',
    'description': """ """,
    'depends': ['event_barcode', 'barcodes_mobile'],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'event_barcode_mobile/static/src/js/**/*',
        ],
        'web.assets_qweb': [
            'event_barcode_mobile/static/src/xml/**/*',
        ],
    }
}
