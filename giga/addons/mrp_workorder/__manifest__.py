# -*- encoding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'MRP II',
    'version': '1.0',
    'category': 'Manufacturing/Manufacturing',
    'sequence': 51,
    'summary': """Work Orders, Planning, Stock Reports.""",
    'depends': ['quality', 'mrp', 'barcodes'],
    'description': """Enterprise extension for MRP
* Work order planning.  Check planning by Gantt views grouped by production order / work center
* Traceability report
* Cost Structure report (mrp_account)""",
    'data': [
        'security/ir.model.access.csv',
        'security/mrp_workorder_security.xml',
        'data/mrp_workorder_data.xml',
        'views/quality_views.xml',
        'views/mrp_bom_views.xml',
        'views/mrp_production_views.xml',
        'views/mrp_workorder_views.xml',
        'views/mrp_workcenter_views.xml',
        'views/res_config_settings_view.xml',
        'wizard/additional_product_views.xml'
    ],
    'demo': [
        'data/mrp_production_demo.xml',
        'data/mrp_workorder_demo.xml'
    ],
    'application': False,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'mrp_workorder/static/src/scss/empty_screen.scss',
            'mrp_workorder/static/src/scss/tablet_view.scss',
            'mrp_workorder/static/src/js/mrp_workorder.js',
            'mrp_workorder/static/src/js/pdf_viewer_no_reload.js',
            'mrp_workorder/static/src/js/viewer_common.js',
            'mrp_workorder/static/src/js/pdf_viewer_widget.js',
            'mrp_workorder/static/src/js/embed_viewer_widget.js',
        ],
        'web.qunit_suite_tests': [
            'mrp_workorder/static/tests/**/*',
        ],
        'web.assets_qweb': [
            'mrp_workorder/static/src/xml/**/*',
        ],
    }
}
