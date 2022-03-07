# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import http
from giga.http import request
from giga.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleStockWishlist(WebsiteSale):
    @http.route(['/shop/wishlist/notify/<model("product.wishlist"):wish>'], type='json', auth="public", website=True)
    def notify_stock(self, wish, notify=True, **kw):
        if not request.website.is_public_user():
            wish['stock_notification'] = notify
        return wish['stock_notification']
