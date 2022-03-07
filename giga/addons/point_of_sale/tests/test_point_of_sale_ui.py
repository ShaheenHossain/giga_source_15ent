# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga.tests import HttpCase, tagged
from giga import tools


@tagged('post_install', '-at_install')
class TestUi(HttpCase):

	# Avoid "A Chart of Accounts is not yet installed in your current company."
	# Everything is set up correctly even without installed CoA
    @tools.mute_logger('giga.http')
    def test_01_point_of_sale_tour(self):

        self.start_tour("/web", 'point_of_sale_tour', login="admin")
