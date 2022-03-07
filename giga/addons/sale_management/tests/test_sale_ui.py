import giga.tests
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.


@giga.tests.tagged('post_install', '-at_install')
class TestUi(giga.tests.HttpCase):

    def test_01_sale_tour(self):
        self.start_tour("/web", 'sale_tour', login="admin", step_delay=100)
