# coding: utf-8
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    "name": "Giga Mexican Localization Reports for Closing",
    'icon': '/l10n_mx/static/description/icon.png',
    "summary": """
        Allow to generate the trial balance for the closing entry.

        Colloquially known as "Month 13"
    """,
    "version": "0.1",
    "author": "Vauxoo",
    "category": "Accounting/Localizations/Reporting",
    "website": "http://www.vauxoo.com",
    "license": "OEEL-1",
    "depends": [
        "l10n_mx_reports",
    ],
    "demo": [
    ],
    "data": [
        "data/l10n_mx_reports_closing_data.xml",
        "views/account_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
