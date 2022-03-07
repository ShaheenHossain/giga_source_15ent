# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import giga.tests
from giga.tools import mute_logger


@giga.tests.common.tagged('post_install', '-at_install')
class TestCustomSnippet(giga.tests.HttpCase):

    @mute_logger('giga.addons.http_routing.models.ir_http', 'giga.http')
    def test_01_run_tour(self):
        self.start_tour("/", 'test_custom_snippet', login="admin")
