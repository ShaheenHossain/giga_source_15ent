# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Belgium - Disallowed Expenses Data',
    'icon': '/l10n_be/static/description/icon.png',
    'version': '1.1',
    'category': 'Accounting/Accounting',
    'description': """
        Disallowed Expenses Data for Belgium
    """,
    'depends': [
        'l10n_be',
        'account_disallowed_expenses',
    ],
    'data': [
        'data/account_disallowed_expenses.xml',
    ],
    'installable': True,
    'auto_install': True,
    'website': 'https://www.gigasource.de/app/accounting',
    'license': 'OEEL-1',
}
