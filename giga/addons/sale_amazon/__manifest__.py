# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

{
    'name': "Amazon Connector",
    'summary': "Import Amazon orders and sync deliveries",
    'description': """
Import your Amazon orders in Giga and synchronize deliveries
============================================================

Key Features
------------
* Import orders from multiple accounts and marketplaces.
* Orders are matched with Giga products based on their internal reference (SKU in Amazon).
* Deliveries confirmed in Giga are synchronized in Amazon.
* Support for both Fulfilment by Amazon (FBA) and Fulfilment by Merchant (FBM):
    * FBA: A stock location and stock moves allow to monitor your stock in Amazon Fulfilment Centers.
    * FBM: Delivery notifications are sent to Amazon for each confirmed picking (partial delivery friendly).
""",
    'category': 'Sales/Sales',
    'sequence': 320,
    'version': '1.1',
    'application': True,
    'depends': ['sale_management', 'stock', 'delivery'],
    'data': [
        'security/ir.model.access.csv',
        'security/sale_amazon_security.xml',
        'data/amazon_data.xml',
        'data/amazon_cron.xml',
        'data/mail_template_data.xml',
        'views/amazon_account_views.xml',
        'views/amazon_marketplace_views.xml',
        'views/amazon_offer_views.xml',
        'views/product_views.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
    ],
    'license': 'OEEL-1',
}
