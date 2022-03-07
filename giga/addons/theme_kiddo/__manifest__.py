{
    'name': 'Kiddo Theme',
    'description': 'Kiddo theme for Giga Website',
    'category': 'Theme/Retail',
    'summary': 'Nursery, Toys, Games, Kids, Boys, Girls, Stores',
    'sequence': 290,
    'version': '2.1.0',
    'author': 'Giga Source ERP',
    'depends': ['theme_common'],
    'data': [
        'data/ir_asset.xml',
        'views/images_library.xml',

        'views/snippets/s_banner.xml',
        'views/snippets/s_image_text.xml',
        'views/snippets/s_picture.xml',
        'views/snippets/s_product_list.xml',
        'views/snippets/s_call_to_action.xml',
        'views/snippets/s_cover.xml',
    ],
    'images': [
        'static/description/Kiddo_description.png',
        'static/description/kiddo_screenshot.jpg',
    ],
    'images_preview_theme': {
        'website.s_banner_default_image': '/theme_kiddo/static/src/img/snippets/s_banner.jpg',
        'website.s_picture_default_image': '/theme_kiddo/static/src/img/content/content_img_15.jpg',
    },
    'snippet_lists': {
        'homepage': ['s_banner', 's_image_text', 's_picture', 's_product_list', 's_call_to_action'],
    },
    'license': 'LGPL-3',
    'live_test_url': 'https://theme-kiddo.gigasource.de',
    'assets': {
        'website.assets_editor': [
            'theme_kiddo/static/src/js/tour.js',
        ],
    }
}
