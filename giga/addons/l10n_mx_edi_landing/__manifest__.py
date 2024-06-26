# coding: utf-8
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': 'Giga Mexico Localization for Stock/Landing',
    'icon': '/l10n_mx/static/description/icon.png',
    'summary': '''
Generate Electronic Invoice with custom numbers
    ''',
    'version': '1.0',
    'category': 'Accounting/Localizations/EDI',
    'depends': [
        'stock_landed_costs',
        'sale_management',
        'sale_stock',
        'l10n_mx_edi_extended',
    ],
    'data': [
        'views/stock_landed_cost.xml',
    ],
    'installable': True,
    'license': 'OEEL-1',
}
