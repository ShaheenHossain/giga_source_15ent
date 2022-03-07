# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga.tests import tagged
from giga.addons.auth_totp.tests.test_totp import TestTOTP


@tagged('post_install', '-at_install')
class TestTOTPInvite(TestTOTP):

    def test_totp_administration(self):
        self.start_tour('/web', 'totp_admin_invite', login='admin')
        self.start_tour('/web', 'totp_admin_self_invite', login='admin')
