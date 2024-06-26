# -*- encoding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quality Worksheet for Workorder',
    'version': '1.0',
    'category': 'Manufacturing/Quality',
    'summary': 'Quality Worksheet for Workorder',
    'depends': ['quality_control_worksheet', 'mrp_workorder'],
    'description': """
    Create customizable quality worksheet for workorder.
""",
    "data": [
        'views/mrp_workorder_views.xml',
    ],
    "demo": [
        'data/mrp_workorder_demo.xml',
    ],
    'auto_install': True,
    'license': 'OEEL-1',
}
