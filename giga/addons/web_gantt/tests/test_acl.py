# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from lxml import etree

from giga.addons.base.tests.common import TransactionCaseWithUserDemo


class TestACL(TransactionCaseWithUserDemo):
    def setUp(self):
        super().setUp()
        self.user_manager = self.env['res.users'].create({
            'login': 'demo123',
            'password': 'demo',
            'partner_id': self.partner_demo.id,
            'groups_id': [(6, 0, [self.env.ref('base.group_system').id])],
        })
        self.env["ir.ui.view"].create({
            "name": "Add delete attribute on gantt view",
            "model": "res.company",
            "type": 'gantt',
            "arch": """
                <gantt date_start="date" date_stop="" string="Test">
                    <field name="partner_id"/>
                </gantt>
            """,
        })

    def test_view_delete_button_visibility(self):
        # the demo user can't unlink
        company_view = self.env['res.company']\
            .with_user(self.user_demo)\
            .fields_view_get(False, 'gantt')
        view_arch = etree.fromstring(company_view['arch'])
        self.assertEqual(view_arch.get('delete'), 'false')

        # the manager user can unlink
        company_view = self.env['res.company']\
            .with_user(self.user_manager)\
            .fields_view_get(False, 'gantt')
        view_arch = etree.fromstring(company_view['arch'])
        self.assertIsNone(view_arch.get('delete'))

