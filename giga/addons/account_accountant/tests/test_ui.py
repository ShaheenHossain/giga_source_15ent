# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import giga.tests


@giga.tests.tagged('-at_install', 'post_install')
class TestUi(giga.tests.HttpCase):
    def test_accountant_tour(self):
        self.start_tour("/web", 'account_accountant_tour', login="admin")
