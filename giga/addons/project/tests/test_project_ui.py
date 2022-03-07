# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import giga.tests


@giga.tests.tagged('post_install', '-at_install')
class TestUi(giga.tests.HttpCase):

    def test_01_project_tour(self):
        self.start_tour("/web", 'project_tour', login="admin")
