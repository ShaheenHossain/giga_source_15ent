# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Switzerland - Accounting Reports',
    'icon': '/l10n_ch/static/description/icon.png',
    'version': '1.1',
    'category': 'Accounting/Localizations/Reporting',
    'description': """
        Accounting reports for Switzerland
    """,
    'depends': [
        'l10n_ch', 'account_reports'
    ],
    'data': [
        'data/account_financial_html_report_data.xml',
    ],
    'installable': True,
    'auto_install': True,
    'website': 'https://www.gigasource.de/app/accounting',
    'license': 'OEEL-1',
}
