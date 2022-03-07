# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from .common import SpreadsheetTestCommon

from giga.tests import tagged
from giga.tests.common import HttpCase

@tagged("post_install", "-at_install")
class TestSpreadsheetOpenPivot(SpreadsheetTestCommon, HttpCase):

    def test_01_spreadsheet_open_pivot_as_admin(self):
        self.start_tour("/web", "spreadsheet_open_pivot_sheet", login="admin")

    def test_01_spreadsheet_open_pivot_as_user(self):
        self.start_tour("/web", "spreadsheet_open_pivot_sheet", login="spreadsheetDude")
