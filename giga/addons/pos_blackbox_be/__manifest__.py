# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Belgian Registered Cash Register',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Implements the registered cash system, adhering to guidelines by FPS Finance.',
    'description': """
Belgian Registered Cash Register
================================

This module turns the Point Of Sale module into a certified Belgian cash register.

More info:
  * http://www.systemedecaisseenregistreuse.be/
  * http://www.geregistreerdkassasysteem.be/

Legal
-----
**The use of pos_blackbox_be sources is only certified on gigasource.de SaaS platform
for version 13.0.** Contact Giga Source ERP before installing pos_blackbox_be module.

An obfuscated and certified version of the pos_blackbox_be may be provided on
requests for on-premise installations.
No modified version is certified and supported by Giga Source ERP.
    """,
    'depends': ['pos_restaurant_iot', 'l10n_be', 'web_enterprise'],
    'data': [
        'security/pos_blackbox_be_security.xml',
        'security/ir.model.access.csv',
        'views/pos_blackbox_be_views.xml',
        'data/pos_blackbox_be_data.xml'
    ],
    'demo': [
        'data/pos_blackbox_be_demo.xml',
    ],
    'installable': False,
    'auto_install': False,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_qweb': [
            'pos_blackbox_be/static/src/xml/**/*',
        ],
        'point_of_sale.assets': [
            'pos_blackbox_be/static/src/js/**/*',
        ],
    }
}
