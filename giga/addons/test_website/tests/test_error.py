import giga.tests
from giga.tools import mute_logger


@giga.tests.common.tagged('post_install', '-at_install')
class TestWebsiteError(giga.tests.HttpCase):

    @mute_logger('giga.addons.http_routing.models.ir_http', 'giga.http')
    def test_01_run_test(self):
        self.start_tour("/test_error_view", 'test_error_website')
