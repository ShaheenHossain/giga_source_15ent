# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from freezegun import freeze_time

from giga.exceptions import ValidationError
from giga.fields import Command
from giga.tests import tagged
from giga.tools import mute_logger

from .common import PayULatamCommon
from ..controllers.main import PayuLatamController
from ..models.payment_acquirer import SUPPORTED_CURRENCIES


@tagged('post_install', '-at_install')
class PayULatamTest(PayULatamCommon):

    def test_compatibility_with_supported_currencies(self):
        """ Test that the PayULatam acquirer is compatible with all supported currencies. """
        for supported_currency_code in SUPPORTED_CURRENCIES:
            supported_currency = self._prepare_currency(supported_currency_code)
            compatible_acquirers = self.env['payment.acquirer']._get_compatible_acquirers(
                self.company.id, self.partner.id, currency_id=supported_currency.id,
            )
            self.assertIn(self.payulatam, compatible_acquirers)

    def test_incompatibility_with_unsupported_currency(self):
        """ Test that the PayULatam acquirer is not compatible with an unsupported currency. """
        compatible_acquirers = self.env['payment.acquirer']._get_compatible_acquirers(
            self.company.id, self.partner.id, currency_id=self.currency_euro.id,
        )
        self.assertNotIn(self.payulatam, compatible_acquirers)

    @freeze_time('2011-11-02 12:00:21')  # Freeze time for consistent singularization behavior
    def test_reference_is_singularized(self):
        """ Test singularization of reference prefixes. """
        reference = self.env['payment.transaction']._compute_reference(self.payulatam.provider)
        self.assertEqual(
            reference, 'tx-20111102120021', "transaction reference was not correctly singularized"
        )

    @freeze_time('2011-11-02 12:00:21')  # Freeze time for consistent singularization behavior
    def test_reference_is_computed_based_on_document_name(self):
        """ Test computation of reference prefixes based on the provided invoice. """
        invoice = self.env['account.move'].create({})
        reference = self.env['payment.transaction']._compute_reference(
            self.payulatam.provider, invoice_ids=[Command.set([invoice.id])]
        )
        self.assertEqual(reference, 'MISC/2011/11/0001-20111102120021')

    def test_redirect_form_values(self):
        """ Test the values of the redirect form inputs. """
        tx = self.create_transaction(flow='redirect')
        with mute_logger('giga.addons.payment.models.payment_transaction'):
            processing_values = tx._get_processing_values()

        form_info = self._extract_values_from_html_form(processing_values['redirect_form_html'])
        expected_values = {
            'merchantId': 'dummy',
            'accountId': 'dummy',
            'description': self.reference,
            'referenceCode': self.reference,
            'amount': str(self.amount),
            'currency': self.currency.name,
            'tax': str(0),
            'taxReturnBase': str(0),
            'buyerEmail': self.partner.email,
            'buyerFullName': self.partner.name,
            'responseUrl': self._build_url(PayuLatamController._return_url),
            'test': str(1),  # testing is always performed in test mode
        }
        expected_values['signature'] = self.payulatam._payulatam_generate_sign(
            expected_values, incoming=False
        )

        self.assertEqual(
            form_info['action'], 'https://sandbox.checkout.payulatam.com/ppp-web-gateway-payu/'
        )
        self.assertDictEqual(form_info['inputs'], expected_values)

    def test_feedback_processing(self):
        # typical data posted by payulatam after client has successfully paid
        payulatam_post_data = {
            'installmentsNumber': '1',
            'lapPaymentMethod': 'VISA',
            'description': self.reference,
            'currency': self.currency.name,
            'extra2': '',
            'lng': 'es',
            'transactionState': '7',
            'polPaymentMethod': '211',
            'pseCycle': '',
            'pseBank': '',
            'referenceCode': self.reference,
            'reference_pol': '844164756',
            'signature': 'f3ea3a7414a56d8153c425ab7e2f69d7',  # Update me
            'pseReference3': '',
            'buyerEmail': 'admin@yourcompany.example.com',
            'lapResponseCode': 'PENDING_TRANSACTION_CONFIRMATION',
            'pseReference2': '',
            'cus': '',
            'orderLanguage': 'es',
            'TX_VALUE': str(self.amount),
            'risk': '',
            'trazabilityCode': '',
            'extra3': '',
            'pseReference1': '',
            'polTransactionState': '14',
            'polResponseCode': '25',
            'merchant_name': 'Test PayU Test comercio',
            'merchant_url': 'http://pruebaslapv.xtrweb.com',
            'extra1': '/shop/payment/validate',
            'message': 'PENDING',
            'lapPaymentMethodType': 'CARD',
            'polPaymentMethodType': '7',
            'telephone': '7512354',
            'merchantId': 'dummy',
            'transactionId': 'b232989a-4aa8-42d1-bace-153236eee791',
            'authorizationCode': '',
            'lapTransactionState': 'PENDING',
            'TX_TAX': '.00',
            'merchant_address': 'Av 123 Calle 12'
        }

        # should raise error about unknown tx
        with self.assertRaises(ValidationError):
            self.env['payment.transaction']._handle_feedback_data('payulatam', payulatam_post_data)

        tx = self.create_transaction(flow='redirect')

        # Validate the transaction ('pending' state)
        self.env['payment.transaction']._handle_feedback_data('payulatam', payulatam_post_data)
        self.assertEqual(tx.state, 'pending', 'Payulatam: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.state_message, payulatam_post_data['message'], 'Payulatam: wrong state message after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'b232989a-4aa8-42d1-bace-153236eee791', 'Payulatam: wrong txn_id after receiving a valid pending notification')

        # Reset the transaction
        tx.write({
            'state': 'draft',
            'acquirer_reference': False})

        # Validate the transaction ('approved' state)
        payulatam_post_data['lapTransactionState'] = 'APPROVED'
        self.env['payment.transaction']._handle_feedback_data('payulatam', payulatam_post_data)
        self.assertEqual(tx.state, 'done', 'Payulatam: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'b232989a-4aa8-42d1-bace-153236eee791', 'Payulatam: wrong txn_id after receiving a valid pending notification')
