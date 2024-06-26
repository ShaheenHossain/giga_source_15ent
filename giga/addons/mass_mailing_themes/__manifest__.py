# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mass Mailing Themes',
    'summary': 'Design gorgeous mails',
    'description': """
Design gorgeous mails
    """,
    'version': '1.1',
    'sequence': 110,
    'website': 'https://www.gigasource.de/app/mailing',
    'category': 'Marketing/Email Marketing',
    'depends': [
        'mass_mailing',
    ],
    'data': [
        'views/mass_mailing_themes_templates.xml'
    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}
