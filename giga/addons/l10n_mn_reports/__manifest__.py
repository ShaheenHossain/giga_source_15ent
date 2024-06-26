# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    "name" : "Mongolia - Accounting Reports",
    'icon': '/l10n_mn/static/description/icon.png',
    "version" : "1.0",
    'category': 'Accounting/Localizations/Reporting',
    "author" : "BumanIT LLC, Giga Source ERP",
    "description": """
Mongolian accounting reports.
====================================================
-Profit and Loss
-Balance Sheet
-Cash Flow Statement
-VAT Repayment Report
-Corporate Revenue Tax Report

Financial requirement contributor: Baskhuu Lodoikhuu. BumanIT LLC
""",
    "depends": ['l10n_mn', 'account_reports'],
    'data': [
        'data/balancesheet_report.xml',
        'data/cashflow_report.xml',
        'data/profit_and_loss_reports.xml',
        'data/vat_report.xml',
        'data/tax_report.xml'
    ],
    'auto_install': True,
    'installable': True,
    'license': 'OEEL-1',
}
