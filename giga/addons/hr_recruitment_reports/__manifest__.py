# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Recruitment Reporting',
    'version': '1.0',
    'category': 'Human Resources/Recruitment',
    'description': """
Add a dynamic report about recruitment.
    """,
    'website': 'https://www.gigasource.de/app/recruitment',
    'depends': ['hr_recruitment', 'web_dashboard'],
    'data': [
        'security/ir.model.access.csv',
        'report/hr_recruitment_report_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}
