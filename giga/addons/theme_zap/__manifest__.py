{
    'name': 'Zap Theme',
    'description': 'Zap Theme - Corporate, Business, Marketing, Copywriting',
    'category': 'Theme/Corporate',
    'summary': 'Digital, Marketing, Copywriting, Media, Events, Non Profit, NGO, Corporate, Business, Services',
    'sequence': 160,
    'version': '2.0.0',
    'author': 'Giga Source ERP',
    'depends': ['theme_common'],
    'data': [
        'data/ir_asset.xml',
        'views/images_library.xml',

        'views/snippets/s_banner.xml',
        'views/snippets/s_call_to_action.xml',
        'views/snippets/s_color_blocks_2.xml',
        'views/snippets/s_cover.xml',
        'views/snippets/s_features.xml',
        'views/snippets/s_masonry_block.xml',
        'views/snippets/s_media_list.xml',
        'views/snippets/s_numbers.xml',
        'views/snippets/s_references.xml',
        'views/snippets/s_image_text.xml',
        'views/snippets/s_three_columns.xml',
    ],
    'images': [
        'static/description/zap_cover.gif',
        'static/description/zap_screenshot.jpg',
    ],
    'images_preview_theme': {
        'website.s_banner_default_image': '/theme_zap/static/src/img/content/banner.jpg',
        'website.s_three_columns_default_image_1': '/theme_zap/static/src/img/content/three_columns_01.jpg',
        'website.s_three_columns_default_image_2': '/theme_zap/static/src/img/content/three_columns_02.jpg',
        'website.s_three_columns_default_image_3': '/theme_zap/static/src/img/content/three_columns_03.jpg',
        'website.library_image_08': '/theme_zap/static/src/img/backgrounds/01.jpg',
        'website.s_masonry_block_default_image_1': '/theme_zap/static/src/img/backgrounds/16.jpg',
        'website.library_image_02': '/theme_zap/static/src/img/content/masonry_block_02.jpg',
    },
    'snippet_lists': {
        'homepage': ['s_banner', 's_three_columns', 's_color_blocks_2', 's_features', 's_masonry_block', 's_references'],
    },
    'license': 'LGPL-3',
    'live_test_url': 'https://theme-zap.gigasource.de',
    'assets': {
        'website.assets_editor': [
            'theme_zap/static/src/js/tour.js',
        ],
    }
}
