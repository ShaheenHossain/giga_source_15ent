import giga.tests
from giga.tools import mute_logger


@giga.tests.common.tagged('post_install', '-at_install')
class TestWebsiteSession(giga.tests.HttpCase):

    def test_01_run_test(self):
        self.start_tour('/', 'test_json_auth')
