# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga.addons.account.tests.common import AccountTestInvoicingCommon
from giga.tests import Form, tagged

from datetime import datetime


@tagged('post_install', '-at_install')
class TestPurchaseOrderReport(AccountTestInvoicingCommon):

    def test_00_purchase_order_report(self):
        uom_dozen = self.env.ref('uom.product_uom_dozen')

        po = self.env['purchase.order'].create({
            'partner_id': self.partner_a.id,
            'currency_id': self.currency_data['currency'].id,
            'order_line': [
                (0, 0, {
                    'name': self.product_a.name,
                    'product_id': self.product_a.id,
                    'product_qty': 1.0,
                    'product_uom': uom_dozen.id,
                    'price_unit': 100.0,
                    'date_planned': datetime.today(),
                    'taxes_id': False,
                }),
                (0, 0, {
                    'name': self.product_b.name,
                    'product_id': self.product_b.id,
                    'product_qty': 1.0,
                    'product_uom': uom_dozen.id,
                    'price_unit': 200.0,
                    'date_planned': datetime.today(),
                    'taxes_id': False,
                }),
            ],
        })
        po.button_confirm()

        f = Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        f.invoice_date = f.date
        f.partner_id = po.partner_id
        f.purchase_id = po
        invoice = f.save()
        invoice.action_post()
        po.flush()

        res_product1 = self.env['purchase.report'].search([
            ('order_id', '=', po.id),
            ('product_id', '=', self.product_a.id),
            ('company_id', '=', self.company_data['company'].id),
        ])

        # check that report will convert dozen to unit or not
        self.assertEqual(res_product1.qty_ordered, 12.0, 'UoM conversion is not working')
        # report should show in company currency (amount/rate) = (100/2)
        self.assertEqual(res_product1.price_total, 50.0, 'Currency conversion is not working')

        res_product2 = self.env['purchase.report'].search([
            ('order_id', '=', po.id),
            ('product_id', '=', self.product_b.id),
            ('company_id', '=', self.company_data['company'].id),
        ])

        self.assertEqual(res_product2.qty_ordered, 1.0, 'No conversion needed since product_b is already a dozen')
        # report should show in company currency (amount/rate) = (200/2)
        self.assertEqual(res_product2.price_total, 100.0, 'Currency conversion is not working')
