# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from unittest.mock import patch, Mock

from giga import fields
from giga.exceptions import UserError
from giga.tools import mute_logger

from giga.addons.sale_amazon.tests.common import TestAmazonCommon, BASE_ORDER_DATA, BASE_ITEM_DATA
from giga.addons.stock.tests.common import TestStockCommon


class TestStock(TestAmazonCommon, TestStockCommon):

    # As this test class is exclusively intended to test Amazon-related check on pickings, the
    # normal flows of stock are put aside in favor of manual updates on quantities.

    def setUp(self):
        super().setUp()

        # Create sales order
        partner = self.env['res.partner'].create({
            'name': "Gederic Frilson",
        })
        self.sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'name': 'test',
                'product_id': self.productA.id,
                'product_uom_qty': 2,
                'amazon_item_ref': '123456789',
            })],
            'amazon_order_ref': '123456789',
        })

        # Create picking
        self.picking = self.PickingObj.create({
            'picking_type_id': self.picking_type_in,
            'location_id': self.supplier_location,
            'location_dest_id': self.customer_location,
        })
        move_vals = {
            'name': self.productA.name,
            'product_id': self.productA.id,
            'product_uom_qty': 1,
            'product_uom': self.productA.uom_id.id,
            'picking_id': self.picking.id,
            'location_id': self.supplier_location,
            'location_dest_id': self.customer_location,
            'sale_line_id': self.sale_order.order_line[0].id,
        }
        self.move_1 = self.MoveObj.create(move_vals)
        self.move_2 = self.MoveObj.create(move_vals)
        self.picking.sale_id = self.sale_order.id  # After creating the moves as it clears the field

    def test_confirm_picking_trigger_SOL_check(self):
        """ Test that confirming a picking triggers a check on sales order lines completion. """

        with patch(
            'giga.addons.sale_amazon.models.stock_picking.StockPicking'
            '._check_sales_order_line_completion', new=Mock()
        ) as mock:
            self.picking.date_done = fields.Datetime.now()  # Trigger the check for SOL completion
            self.assertEqual(
                mock.call_count, 1, "confirming a picking should trigger a check on the sales "
                                    "order lines completion"
            )

    def test_check_SOL_completion_no_move(self):
        """ Test that the check on SOL completion passes if no move is confirmed. """

        self.assertIsNone(
            self.picking._check_sales_order_line_completion(),
            "the check of SOL completion should not raise for pickings with completions of 0% (no"
            "confirmed move for a given sales order line)"
        )

    def test_check_SOL_completion_all_moves(self):
        """ Test that the check on SOL completion passes if all moves are confirmed. """

        self.move_1.quantity_done = 1
        self.move_2.quantity_done = 1
        self.assertIsNone(
            self.picking._check_sales_order_line_completion(),
            "the check of SOL completion should not raise for pickings with completions of 100% "
            "(all moves related to a given sales order line are confirmed)"
        )

    def test_check_SOL_completion_some_moves(self):
        """ Test that the check on SOL completion fails if only some moves are confirmed. """

        self.move_1.quantity_done = 1
        with self.assertRaises(UserError):
            # The check of SOL completion should raise for pickings with completions of ]0%, 100%[
            # (some moves related to a given sales order line are confirmed, but not all)
            self.picking._check_sales_order_line_completion()

    @mute_logger('giga.addons.sale_amazon.models.amazon_account')
    @mute_logger('giga.addons.sale_amazon.models.stock_picking')
    def test_check_carrier_details_compliance_no_carrier(self):
        """ Test the validation of a picking when the delivery carrier is not set. """
        def _get_orders_data_mock(*_args, **_kwargs):
            """ Return a one-order batch of test order data without calling MWS API. """
            return [BASE_ORDER_DATA], datetime(2020, 1, 1), None, False

        def _get_items_data_mock(*_args, **_kwargs):
            """ Return a one-item batch of test order line data without calling MWS API. """
            return [BASE_ITEM_DATA], None, False

        with patch('giga.addons.sale_amazon.models.mws_connector.get_api_connector',
                   new=lambda *args, **kwargs: None), \
             patch('giga.addons.sale_amazon.models.mws_connector.get_orders_data',
                   new=_get_orders_data_mock), \
             patch('giga.addons.sale_amazon.models.mws_connector.get_items_data',
                   new=_get_items_data_mock), \
             patch('giga.addons.sale_amazon.models.mws_connector.submit_feed',
                   new=Mock(return_value=(0, False))):
            self.account._sync_orders(auto_commit=False)
            order = self.env['sale.order'].search([('amazon_order_ref', '=', '123456789')])
            picking = self.env['stock.picking'].search([('sale_id', '=', order.id)])
            picking.carrier_id = None
            picking.carrier_tracking_ref = "dummy tracking ref"
            picking.location_dest_id.usage = 'customer'
            with self.assertRaises(UserError):
                picking._check_carrier_details_compliance()

    @mute_logger('giga.addons.sale_amazon.models.amazon_account')
    @mute_logger('giga.addons.sale_amazon.models.stock_picking')
    def test_check_carrier_details_compliance_intermediate_delivery_step(self):
        """ Test the validation of a picking when the delivery is in an intermediate step."""
        def _get_orders_data_mock(*_args, **_kwargs):
            """ Return a one-order batch of test order data without calling MWS API. """
            return [BASE_ORDER_DATA], datetime(2020, 1, 1), None, False

        def _get_items_data_mock(*_args, **_kwargs):
            """ Return a one-item batch of test order line data without calling MWS API. """
            return [BASE_ITEM_DATA], None, False

        with patch('giga.addons.sale_amazon.models.mws_connector.get_api_connector',
                   new=lambda *args, **kwargs: None), \
             patch('giga.addons.sale_amazon.models.mws_connector.get_orders_data',
                   new=_get_orders_data_mock), \
             patch('giga.addons.sale_amazon.models.mws_connector.get_items_data',
                   new=_get_items_data_mock), \
             patch('giga.addons.sale_amazon.models.mws_connector.submit_feed',
                   new=Mock(return_value=(0, False))):
            self.account._sync_orders(auto_commit=False)
            order = self.env['sale.order'].search([('amazon_order_ref', '=', '123456789')])
            picking = self.env['stock.picking'].search([('sale_id', '=', order.id)])
            picking.carrier_id = None
            picking.carrier_tracking_ref = "dummy tracking ref"
            intermediate_destination_id = self.env.ref('stock.location_pack_zone').id
            picking.location_dest_id = intermediate_destination_id
            picking._check_carrier_details_compliance()  # Don't raise if intermediate delivery step

    @mute_logger('giga.addons.sale_amazon.models.amazon_account')
    @mute_logger('giga.addons.sale_amazon.models.stock_picking')
    def test_check_carrier_details_compliance_no_tracking_number(self):
        """ Test the validation of a picking when the tracking reference is not set. """
        def _get_orders_data_mock(*_args, **_kwargs):
            """ Return a one-order batch of test order data without calling MWS API. """
            return [BASE_ORDER_DATA], datetime(2020, 1, 1), None, False

        def _get_items_data_mock(*_args, **_kwargs):
            """ Return a one-item batch of test order line data without calling MWS API. """
            return [BASE_ITEM_DATA], None, False

        with patch('giga.addons.sale_amazon.models.mws_connector.get_api_connector',
                   new=lambda *args, **kwargs: None), \
             patch('giga.addons.sale_amazon.models.mws_connector.get_orders_data',
                   new=_get_orders_data_mock), \
             patch('giga.addons.sale_amazon.models.mws_connector.get_items_data',
                   new=_get_items_data_mock), \
             patch('giga.addons.sale_amazon.models.mws_connector.submit_feed',
                   new=Mock(return_value=(0, False))):
            self.account._sync_orders(auto_commit=False)
            order = self.env['sale.order'].search([('amazon_order_ref', '=', '123456789')])
            picking = self.env['stock.picking'].search([('sale_id', '=', order.id)])
            picking.carrier_id = self.carrier
            picking.carrier_tracking_ref = None
            with self.assertRaises(UserError):
                picking._check_carrier_details_compliance()

    @mute_logger('giga.addons.sale_amazon.models.amazon_account')
    @mute_logger('giga.addons.sale_amazon.models.stock_picking')
    def test_check_carrier_details_compliance_requirements_met_in_last_step_delivery(self):
        """ Test the validation of a picking when the delivery carrier and tracking ref are set. """
        def _get_orders_data_mock(*_args, **_kwargs):
            """ Return a one-order batch of test order data without calling MWS API. """
            return [BASE_ORDER_DATA], datetime(2020, 1, 1), None, False

        def _get_items_data_mock(*_args, **_kwargs):
            """ Return a one-item batch of test order line data without calling MWS API. """
            return [BASE_ITEM_DATA], None, False

        with patch('giga.addons.sale_amazon.models.mws_connector.get_api_connector',
                   new=lambda *args, **kwargs: None), \
             patch('giga.addons.sale_amazon.models.mws_connector.get_orders_data',
                   new=_get_orders_data_mock), \
             patch('giga.addons.sale_amazon.models.mws_connector.get_items_data',
                   new=_get_items_data_mock), \
             patch('giga.addons.sale_amazon.models.mws_connector.submit_feed',
                   new=Mock(return_value=(0, False))):
            self.account._sync_orders(auto_commit=False)
            order = self.env['sale.order'].search([('amazon_order_ref', '=', '123456789')])
            picking = self.env['stock.picking'].search([('sale_id', '=', order.id)])
            picking.carrier_id = self.carrier
            picking.carrier_tracking_ref = "dummy tracking ref"
            picking._check_carrier_details_compliance()  # Everything is fine, don't raise
