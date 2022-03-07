# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import giga
from giga.tests import tagged
from giga.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestSpreadsheetTemplate(HttpCase):

    def test_pipeline_revenue_template(self):
        self.start_tour('/web', 'spreadsheet_template_MRR_NRR_pipeline_revenue', login='admin')

    def test_pipeline_template(self):
        self.start_tour('/web', 'spreadsheet_template_pipeline_report', login='admin')
