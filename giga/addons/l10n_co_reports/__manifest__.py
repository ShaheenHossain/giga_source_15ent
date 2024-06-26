# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

# Copyright (C) David Arnold (XOE Solutions).
# Author        David Arnold (XOE Solutions), dar@xoe.solutions
# Co-Authors    Juan Pablo Aries (devCO), jpa@devco.co
#               Hector Ivan Valencia Muñoz (TIX SAS)
#               Nhomar Hernandez (Vauxoo)
#               Humberto Ochoa (Vauxoo)

{
    'name': 'Colombian - Accounting Reports',
    'icon': '/l10n_co/static/description/icon.png',
    'version': '1.1',
    'description': """
Accounting reports for Colombia
================================
    """,
    'author': ['David Arnold (XOE Solutions)'],
    'category': 'Accounting/Localizations/Reporting',
    'depends': ['l10n_co', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'data/l10n_co_reports.xml',
        'wizard/retention_report_views.xml',
        'report/certification_report_templates.xml',
    ],
    'demo': [],
    'auto_install': True,
    'installable': True,
    'website': 'https://xoe.solutions',
    'license': 'OEEL-1',
}
