# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import giga
import giga.tests


@giga.tests.common.tagged('post_install', '-at_install')
class TestSnippets(giga.tests.HttpCase):

    def test_01_newsletter_popup(self):
        self.start_tour("/?enable_editor=1", "newsletter_popup_edition", login='admin')
        self.start_tour("/", "newsletter_popup_use", login=None)
        mailing_list = self.env['mailing.list'].search([], limit=1)
        emails = mailing_list.contact_ids.mapped('email')
        self.assertIn("hello@world.com", emails)
