# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Standard Audit File for Tax Base module',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'description': """
Base module for SAF-T reporting
===============================
This is meant to be used with localization specific modules.
    """,
    'depends': [
        'account_reports'
    ],
    'data': [
        'data/saft_report.xml',
    ],
    'license': 'OEEL-1',
}
