# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk After Sales',
    'category': 'Services/Helpdesk',
    'summary': 'Project, Tasks, After Sales',
    'depends': ['helpdesk', 'sale_management'],
    'auto_install': True,
    'description': """
Manage the after sale of the products from helpdesk tickets.
    """,
    'data': [
        'views/helpdesk_views.xml',
        'report/helpdesk_ticket_analysis_views.xml',
        'report/helpdesk_sla_report_analysis_views.xml',
    ],
    'demo': ['data/helpdesk_sale_demo.xml'],
    'license': 'OEEL-1',
}
