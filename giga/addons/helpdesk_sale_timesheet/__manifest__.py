# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sell Helpdesk Timesheet',
    'category': 'Hidden',
    'summary': 'Project, Helpdesk, Timesheet and Sale Orders',
    'depends': ['helpdesk_timesheet', 'sale_timesheet', 'helpdesk_sale'],
    'description': """
        Bill timesheets logged on helpdesk tickets.
    """,
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk_views.xml',
        'views/helpdesk_portal_templates.xml',
        'views/project_project_views.xml',
        'views/product_views.xml',
        'views/sale_views.xml',
    ],
    'demo': ['data/helpdesk_sale_timesheet_demo.xml'],
    'license': 'OEEL-1',
    'post_init_hook': '_helpdesk_sale_timesheet_post_init'
}
