# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import giga.tests

@giga.tests.tagged("post_install", "-at_install")
class TestGigaEditor(giga.tests.HttpCase):

    def test_giga_editor_suite(self):
        self.browser_js('/web_editor/static/lib/giga-editor/test/editor-test.html', "", "", timeout=1800)
