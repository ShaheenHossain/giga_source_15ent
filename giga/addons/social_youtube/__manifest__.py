# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Social YouTube',
    'category': 'Marketing/Social Marketing',
    'summary': 'Manage your YouTube videos and schedule video uploads',
    'version': '1.0',
    'description': """Manage your YouTube videos and schedule video uploads""",
    'depends': ['social', 'iap'],
    'data': [
        'data/social_media_data.xml',
        'views/res_config_settings_views.xml',
        'views/social_account_views.xml',
        'views/social_post_views.xml',
        'views/social_post_template_views.xml',
        'views/social_stream_post_views.xml',
        'views/social_youtube_templates.xml',
    ],
    # 'auto_install': True,  # temporarily disabled until approved by YouTube
    'assets': {
        'web.assets_backend': [
            'social_youtube/static/src/scss/social_youtube.scss',
            'social_youtube/static/src/js/social_youtube_upload_field.js',
            'social_youtube/static/src/js/stream_post_youtube_comments.js',
            'social_youtube/static/src/js/stream_post_kanban_controller.js',
            ('after', 'social/static/src/js/social_post_formatter_mixin.js', 'social_youtube/static/src/js/social_post_formatter_mixin.js'),
        ],
        'web.assets_qweb': [
            'social_youtube/static/src/xml/**/*',
        ],
    },
    'license': 'OEEL-1',
}
