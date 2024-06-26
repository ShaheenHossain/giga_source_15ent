# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Synchronization with the external timesheet application',
    'version': '1.0',
    'category': 'Services/Project',
    'description': """
Synchronization of timesheet entries with the external timesheet application.
=============================================================================

If you use the external timesheet application, this module alows you to synchronize timesheet entries between Giga and the application.
    """,
    'website': 'https://www.gigasource.de/app/project',
    'images': ['images/invoice_task_work.jpeg', 'images/my_timesheet.jpeg', 'images/working_hour.jpeg'],
    'depends': ['hr_timesheet'],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
    'assets': {
        'web.qunit_suite_tests': [
            'project_timesheet_synchro/static/src/js/project_timesheet.js',
            'project_timesheet_synchro/static/tests/timesheet_app_tests.js',
        ],
        'web.assets_tests': [
            'project_timesheet_synchro/static/tests/tours/**/*',
        ],
        'project_timesheet_synchro.assets_timesheet_app': [
            'project_timesheet_synchro/static/src/css/**/*',
            'web/static/src/legacy/legacy_setup.js',
        ],
    }
}
