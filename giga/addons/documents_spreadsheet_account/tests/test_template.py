# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

import giga
from giga.tests import tagged
from giga.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestSpreadsheetTemplate(HttpCase):

    def test_spreadsheet_template_montly_budget(self):
        self.start_tour('/web', 'spreadsheet_template_montly_budget', login='admin')

    def test_spreadsheet_template_quarterly_budget(self):
        self.start_tour('/web', 'spreadsheet_template_quarterly_budget', login='admin')

    def test_spreadsheet_template_sales_commission(self):
        self.start_tour('/web', 'spreadsheet_template_sales_commission', login='admin')
