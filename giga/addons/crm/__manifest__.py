# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.


{
    'name': 'CRM',
    'version': '1.6',
    'category': 'Sales/CRM',
    'sequence': 15,
    'summary': 'Track leads and close opportunities',
    'description': "",
    'website': 'https://www.gigasource.de/app/crm',
    'depends': [
        'base_setup',
        'sales_team',
        'mail',
        'calendar',
        'resource',
        'fetchmail',
        'utm',
        'web_tour',
        'web_kanban_gauge',
        'contacts',
        'digest',
        'phone_validation',
    ],
    'data': [
        'security/crm_security.xml',
        'security/ir.model.access.csv',

        'data/crm_lead_prediction_data.xml',
        'data/crm_lost_reason_data.xml',
        'data/crm_stage_data.xml',
        'data/crm_team_data.xml',
        'data/digest_data.xml',
        'data/ir_action_data.xml',
        'data/ir_cron_data.xml',
        'data/mail_data.xml',
        'data/crm_recurring_plan_data.xml',

        'wizard/crm_lead_lost_views.xml',
        'wizard/crm_lead_to_opportunity_views.xml',
        'wizard/crm_lead_to_opportunity_mass_views.xml',
        'wizard/crm_merge_opportunities_views.xml',
        'wizard/crm_lead_pls_update_views.xml',

        'views/calendar_views.xml',
        'views/crm_recurring_plan_views.xml',
        'views/crm_lost_reason_views.xml',
        'views/crm_stage_views.xml',
        'views/crm_lead_views.xml',
        'views/crm_team_member_views.xml',
        'views/digest_views.xml',
        'views/mail_activity_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/utm_campaign_views.xml',
        'report/crm_activity_report_views.xml',
        'report/crm_opportunity_report_views.xml',
        'views/crm_team_views.xml',
        'views/crm_menu_views.xml',
        'views/crm_helper_templates.xml',
    ],
    'demo': [
        'data/crm_team_demo.xml',
        'data/mail_template_demo.xml',
        'data/crm_team_member_demo.xml',
        'data/mail_activity_demo.xml',
        'data/crm_lead_demo.xml',
    ],
    'css': ['static/src/css/crm.css'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_qweb': [
            'crm/static/src/xml/forecast_kanban.xml',
        ],
        'web.assets_backend': [
            'crm/static/src/js/crm_form.js',
            'crm/static/src/js/crm_kanban.js',
            'crm/static/src/js/forecast/*',
            'crm/static/src/js/systray_activity_menu.js',
            'crm/static/src/js/tours/crm.js',
            'crm/static/src/scss/crm.scss',
            'crm/static/src/scss/crm_team_member_views.scss',
        ],
        'web.assets_tests': [
            'crm/static/tests/tours/**/*',
        ],
        'web.qunit_suite_tests': [
            'crm/static/tests/mock_server.js',
            'crm/static/tests/forecast_kanban_tests.js',
            'crm/static/tests/forecast_view_tests.js',
            'crm/static/tests/crm_rainbowman_tests.js',
        ],
    },
    'license': 'LGPL-3',
}
