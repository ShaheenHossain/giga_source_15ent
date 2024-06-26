# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Stock',
    'category': 'Services/Helpdesk',
    'summary': 'Project, Tasks, Stock',
    'depends': ['helpdesk_sale', 'stock'],
    'auto_install': False,
    'description': """
Manage Product returns from helpdesk tickets
    """,
    'data': [
        'wizard/stock_picking_return_views.xml',
        'views/helpdesk_views.xml',
        'report/helpdesk_ticket_analysis_views.xml',
        'report/helpdesk_sla_report_analysis_views.xml',
    ],
    'demo': ['data/helpdesk_stock_demo.xml'],
    'license': 'OEEL-1',
}
