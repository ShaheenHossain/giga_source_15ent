# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import giga.tests


@giga.tests.tagged('-at_install', 'post_install')
class WebSuite(giga.tests.HttpCase):
    def test_01_js(self):
        self.browser_js('/web/tests?module=pos_blackbox_be.Order',"","", login='admin')
