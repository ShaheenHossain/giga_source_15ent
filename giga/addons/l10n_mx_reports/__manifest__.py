# coding: utf-8
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    "name": "Giga Mexican Localization Reports",
    'icon': '/l10n_mx/static/description/icon.png',
    "summary": """
        Electronic accounting reports
            - COA
            - Trial Balance
        DIOT Report
    """,
    "version": "1.0",
    "author": "Vauxoo",
    "category": "Accounting/Localizations/Reporting",
    "website": "http://www.vauxoo.com",
    "license": "OEEL-1",
    "depends": [
        "account_reports",
        "l10n_mx",
    ],
    "demo": [
        "demo/res_company_demo.xml",
        "demo/res_partner_demo.xml",
    ],
    "data": [
        "data/account_financial_report_data.xml",
        "data/country_data.xml",
        "data/templates/cfdicoa.xml",
        "data/templates/cfdibalance.xml",
        "views/res_country_view.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
