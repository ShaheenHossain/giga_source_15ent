# -*- coding: utf-8 -*-
from datetime import datetime
import base64
import logging
from freezegun import freeze_time
from lxml import etree
from unittest.mock import patch

from giga.tests import tagged
from giga.tools import misc
from giga.addons.l10n_cl_edi_stock.tests.common import TestL10nClEdiStockCommon
from giga.addons.l10n_cl_edi.tests.common import _check_with_xsd_patch

_logger = logging.getLogger(__name__)


@tagged('post_install_l10n', 'post_install', '-at_install')
@patch('giga.tools.xml_utils._check_with_xsd', _check_with_xsd_patch)
class TestL10nClEdiStock(TestL10nClEdiStockCommon):

    @patch('giga.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_edi_delivery_with_taxes_from_inventory(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-24T20:00:00'
        picking = self.PickingObj.create({
            'name': 'Test Delivery Guide',
            'partner_id': self.chilean_partner_a.id,
            'picking_type_id': self.picking_type_out,
            'location_id': self.stock_location,
            'location_dest_id': self.customer_location,
        })
        self.MoveObj.create({
            'name': self.product_with_taxes_a.name,
            'product_id': self.product_with_taxes_a.id,
            'product_uom': self.product_with_taxes_a.uom_id.id,
            'product_uom_qty': 10.00,
            'procure_method': 'make_to_stock',
            'picking_id': picking.id,
            'location_id': self.stock_location,
            'location_dest_id': self.customer_location,
            'company_id': self.company.id
        })
        self.MoveObj.create({
            'name': self.product_with_taxes_b.name,
            'product_id': self.product_with_taxes_b.id,
            'product_uom': self.product_with_taxes_b.uom_id.id,
            'product_uom_qty': 1,
            'procure_method': 'make_to_stock',
            'picking_id': picking.id,
            'location_id': self.stock_location,
            'location_dest_id': self.customer_location,
            'company_id': self.company.id
        })
        picking.company_id = self.company.id
        picking.scheduled_date = datetime(2019, 10, 24, 20, 0, 0)
        picking.create_delivery_guide()

        self.assertEqual(picking.l10n_cl_dte_status, False)
        self.assertEqual(picking.l10n_cl_draft_status, True)

        picking.l10n_latam_document_number = 100
        picking.l10n_cl_confirm_draft_delivery_guide()

        self.assertEqual(picking.l10n_latam_document_number, '100')
        self.assertEqual(picking.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open('l10n_cl_edi_stock/tests/expected_dtes/delivery_guide_products_with_taxes.xml').read()

        self.assertXmlTreeEqual(
            etree.fromstring(xml_expected_dte.encode()),
            etree.fromstring(base64.b64decode(picking.l10n_cl_sii_send_file.with_context(bin_size=False).datas))
        )

    @freeze_time('2019-10-24')
    @patch('giga.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_edi_delivery_with_taxes_from_sale_order(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-24T20:00:00'

        so_vals = {
            'partner_id': self.chilean_partner_a.id,
            'order_line': [
                (0, 0, {
                'name': self.product_with_taxes_a.name,
                'product_id': self.product_with_taxes_a.id,
                'product_uom_qty': 10.0,
                'product_uom': self.product_with_taxes_a.uom_id.id,
                'price_unit': self.product_with_taxes_a.list_price
                }),
                (0, 0, {
                'name': self.product_with_taxes_b.name,
                'product_id': self.product_with_taxes_b.id,
                'product_uom_qty': 1.0,
                'product_uom': self.product_with_taxes_b.uom_id.id,
                'price_unit': self.product_with_taxes_b.list_price
                })
            ],
            'company_id': self.company.id,
        }
        sale_order = self.env['sale.order'].create(so_vals)
        sale_order.action_confirm()

        picking = sale_order.picking_ids[0]
        picking.action_assign()
        picking.move_lines[0].write({'quantity_done': 10})
        picking.move_lines[1].write({'quantity_done': 1})
        picking.button_validate()

        picking.create_delivery_guide()

        self.assertEqual(picking.l10n_cl_dte_status, False)
        self.assertEqual(picking.l10n_cl_draft_status, True)

        picking.l10n_latam_document_number = 100
        picking.l10n_cl_confirm_draft_delivery_guide()

        self.assertEqual(picking.l10n_latam_document_number, '100')
        self.assertEqual(picking.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open('l10n_cl_edi_stock/tests/expected_dtes/delivery_guide_products_with_taxes.xml').read()

        self.assertXmlTreeEqual(
            etree.fromstring(xml_expected_dte.encode()),
            etree.fromstring(base64.b64decode(picking.l10n_cl_sii_send_file.with_context(bin_size=False).datas))
        )

    @freeze_time('2019-10-24')
    @patch('giga.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_edi_delivery_without_taxes_from_sale_order(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-24T20:00:00'

        so_vals = {
            'partner_id': self.chilean_partner_a.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_without_taxes_a.name,
                    'product_id': self.product_without_taxes_a.id,
                    'product_uom_qty': 5.0,
                    'product_uom': self.product_without_taxes_a.uom_id.id,
                    'price_unit': self.product_without_taxes_a.list_price,
                    'discount': 10.00,
                }),
                (0, 0, {
                    'name': self.product_without_taxes_b.name,
                    'product_id': self.product_without_taxes_b.id,
                    'product_uom_qty': 10.0,
                    'product_uom': self.product_without_taxes_b.uom_id.id,
                    'price_unit': self.product_without_taxes_b.list_price
                })
            ],
            'company_id': self.company.id,
        }
        sale_order = self.env['sale.order'].create(so_vals)
        sale_order.action_confirm()

        picking = sale_order.picking_ids[0]
        picking.action_assign()
        picking.move_lines[0].write({'quantity_done': 5})
        picking.move_lines[1].write({'quantity_done': 10})
        picking.button_validate()

        picking.create_delivery_guide()

        self.assertEqual(picking.l10n_cl_dte_status, False)
        self.assertEqual(picking.l10n_cl_draft_status, True)

        picking.l10n_latam_document_number = 100
        picking.l10n_cl_confirm_draft_delivery_guide()

        self.assertEqual(picking.l10n_latam_document_number, '100')
        self.assertEqual(picking.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open('l10n_cl_edi_stock/tests/expected_dtes/delivery_guide_products_without_taxes.xml').read()

        self.assertXmlTreeEqual(
            etree.fromstring(xml_expected_dte.encode()),
            etree.fromstring(base64.b64decode(picking.l10n_cl_sii_send_file.with_context(bin_size=False).datas))
        )

    @freeze_time('2019-10-24')
    @patch('giga.addons.l10n_cl_edi.models.l10n_cl_edi_util.L10nClEdiUtilMixin._get_cl_current_strftime')
    def test_l10n_cl_edi_delivery_guide_no_price(self, get_cl_current_strftime):
        get_cl_current_strftime.return_value = '2019-10-24T20:00:00'
        copy_chilean_partner = self.chilean_partner_a.copy()
        copy_chilean_partner.write({'l10n_cl_delivery_guide_price': 'none'})
        so_vals = {
            'partner_id': copy_chilean_partner.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_with_taxes_a.name,
                    'product_id': self.product_with_taxes_a.id,
                    'product_uom_qty': 3.0,
                    'product_uom': self.product_with_taxes_a.uom_id.id,
                    'price_unit': self.product_with_taxes_a.list_price,
                    'discount': 10.00,
                })
            ],
            'company_id': self.company.id,
        }
        sale_order = self.env['sale.order'].create(so_vals)
        sale_order.action_confirm()

        picking = sale_order.picking_ids[0]
        picking.action_assign()
        picking.move_lines[0].write({'quantity_done': 3})
        picking.button_validate()

        picking.create_delivery_guide()

        self.assertEqual(picking.l10n_cl_dte_status, False)
        self.assertEqual(picking.l10n_cl_draft_status, True)

        picking.l10n_latam_document_number = 100
        picking.l10n_cl_confirm_draft_delivery_guide()

        self.assertEqual(picking.l10n_latam_document_number, '100')
        self.assertEqual(picking.l10n_cl_dte_status, 'not_sent')

        xml_expected_dte = misc.file_open('l10n_cl_edi_stock/tests/expected_dtes/delivery_guide_no_price.xml').read()

        self.assertXmlTreeEqual(
            etree.fromstring(xml_expected_dte.encode()),
            etree.fromstring(base64.b64decode(picking.l10n_cl_sii_send_file.with_context(bin_size=False).datas))
        )
