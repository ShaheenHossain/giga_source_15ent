# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
{
    'name': "Marketing Automation",
    'version': "1.0",
    'summary': "Build automated mailing campaigns",
    'website': 'https://www.gigasource.de/app/marketing-automation',
    'category': "Marketing/Marketing Automation",
    'sequence': 195,
    'depends': ['mass_mailing'],
    'data': [
        'security/marketing_automation_security.xml',
        'security/ir.model.access.csv',
        'views/ir_actions_views.xml',
        'views/ir_model_views.xml',
        'views/marketing_automation_menus.xml',
        'wizard/marketing_campaign_test_views.xml',
        'views/link_tracker_views.xml',
        'views/mailing_mailing_views.xml',
        'views/mailing_trace_views.xml',
        'views/marketing_activity_views.xml',
        'views/marketing_participant_views.xml',
        'views/marketing_trace_views.xml',
        'views/marketing_campaign_views.xml',
        'data/ir_cron_data.xml',
    ],
    'demo': [
        'data/marketing_automation_demo.xml'
    ],
    'application': True,
    'license': 'OEEL-1',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web._assets_primary_variables': [
            'marketing_automation/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            'marketing_automation/static/src/js/marketing_automation_graph.js',
            'marketing_automation/static/src/js/marketing_automation_one2many.js',
            'marketing_automation/static/src/js/marketing_campaign_view.js',
            'marketing_automation/static/src/js/marketing_campaign_controller.js',
            'marketing_automation/static/src/scss/marketing_automation.scss',
        ],
        'web.qunit_suite_tests': [
            'marketing_automation/static/tests/**/*',
        ],
    }
}
