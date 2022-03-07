import giga.tests

@giga.tests.tagged('-at_install', 'post_install')
class TestUi(giga.tests.HttpCase):
    def test_01_ui(self):
        self.start_tour("/", 'activity_creation', login='admin')

    def test_02_ui(self):
        self.start_tour("/", 'test_screen_navigation', login='admin')
