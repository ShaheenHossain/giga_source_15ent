# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Referral',
    'version': '1.0',
    'category': 'Human Resources/Referrals',
    'sequence': 235,
    'summary': 'Let your employees share job positions and refer their friends',
    'description': """Let your employees share job positions and refer their friends""",
    'website': ' ',
    'depends': ['hr_recruitment', 'link_tracker', 'website_hr_recruitment', 'web_dashboard', 'hr_recruitment_reports'],
    'data': [
        'data/data.xml',
        'security/hr_referral_security.xml',
        'security/ir.model.access.csv',
        'views/hr_applicant_views.xml',
        'wizard/hr_referral_alert_mail_wizard_views.xml',
        'wizard/hr_referral_link_to_share_views.xml',
        'wizard/hr_referral_send_mail_views.xml',
        'views/hr_job_views.xml',
        'views/hr_recruitment_views.xml',
        'views/hr_referral_onboarding_views.xml',
        'views/hr_referral_level_views.xml',
        'views/hr_referral_friend_views.xml',
        'views/hr_referral_alert_views.xml',
        'views/hr_referral_reward_views.xml',
        'views/hr_referral_views.xml',
        'report/hr_referral_report_views.xml',
        'report/hr_recruitment_report_views.xml',
    ],
    'demo': ['data/hr_referral_demo.xml'],
    'installable': True,
    'application': True,
    'pre_init_hook': '_pre_init_referral',
    'post_init_hook': '_update_stage',
    'assets': {
        'web.assets_backend': [
            'hr_referral/static/src/scss/referral_kanban_view.scss',
            'hr_referral/static/src/scss/_fonts.scss',
            'hr_referral/static/src/scss/hr_referral.scss',
            'hr_referral/static/src/scss/hr_onboarding.scss',
            'hr_referral/static/src/scss/progress_bar.scss',
            'hr_referral/static/src/js/hr_referral_dashboard.js',
            'hr_referral/static/src/js/hr_referral_welcome.js',
        ],
        'web.assets_qweb': [
            'hr_referral/static/src/xml/**/*',
        ],
    },
    'license': 'OEEL-1',
}
