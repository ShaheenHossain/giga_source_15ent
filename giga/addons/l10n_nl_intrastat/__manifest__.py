# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Netherlands Intrastat Declaration',
    'icon': '/l10n_nl/static/description/icon.png',
    'category': 'Accounting/Localizations/Reporting',
    'description': """
Generates Netherlands Intrastat report for declaration based on invoices.
    """,
    'depends': ['l10n_nl', 'account_intrastat'],
    'data': [
        'views/res_company_view.xml',
    ],
    'auto_install': True,
    'license': 'OEEL-1',
}
