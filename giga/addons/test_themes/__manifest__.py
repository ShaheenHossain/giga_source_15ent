{
    'name': 'Themes Testing Module',
    'version': '1.0',
    'category': 'Hidden',
    'sequence': 9877,
    'summary': 'Create a new website for each Giga theme for an easy preview.',
    'description': """This module will help you to quickly test all the Giga
    themes without having to switch from one theme to another on your website.
    It will simply create a new website for each Giga theme and install every
    theme on one website.""",
    'depends': [
        # CE themes
        'theme_default',

        # design-themes themes
        'theme_anelusia',
        'theme_artists',
        'theme_avantgarde',
        'theme_aviato',
        'theme_beauty',
        'theme_bewise',
        'theme_bistro',
        'theme_bookstore',
        'theme_buzzy',
        'theme_clean',
        'theme_cobalt',
        'theme_enark',
        'theme_graphene',
        'theme_kea',
        'theme_kiddo',
        'theme_loftspace',
        'theme_monglia',
        'theme_nano',
        'theme_notes',
        'theme_giga_experts',
        'theme_orchid',
        'theme_paptic',
        'theme_real_estate',
        'theme_treehouse',
        'theme_vehicle',
        'theme_yes',
        'theme_zap',
    ],
    'data': [
        'views/website_navbar_templates.xml',
    ],
    'installable': True,
    'application': False,
    'post_init_hook': 'post_init_hook',
    'assets': {
        'web.assets_frontend': [
            'test_themes/static/src/js/navbar.js',
        ],
    },
    'license': 'LGPL-3',
}
