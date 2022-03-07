# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sweden - Accounting Reports',
    'icon': '/l10n_se/static/description/icon.png',
    'version': '1.0',
    'category': 'Accounting/Localizations/Reporting',
    'author': "XCLUDE",
    'website': "https://www.xclude.se",
    'description': """
        Accounting reports for Sweden
    """,
    'depends': [
        'l10n_se', 'account_reports'
    ],
    'data': [
        'views/report_export_template.xml'
    ],
    'installable': True,
    'auto_install': True,
    'website': 'https://www.gigasource.de/app/accounting',
    'license': 'OEEL-1',
}
