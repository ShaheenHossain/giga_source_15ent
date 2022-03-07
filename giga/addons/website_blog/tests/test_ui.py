# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import giga.tests
from giga import tools


@giga.tests.tagged('post_install', '-at_install')
class TestUi(giga.tests.HttpCase):
    def test_admin(self):
        self.env['blog.blog'].create({'name': 'Travel'})
        self.env['ir.attachment'].create({
            'public': True,
            'type': 'url',
            'url': '/web/image/123/transparent.png',
            'name': 'transparent.png',
            'mimetype': 'image/png',
        })
        self.start_tour("/", 'blog', login='admin')
