# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga.addons.payment.tests.common import PaymentCommon


class SipsCommon(PaymentCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.sips = cls._prepare_acquirer('sips', update_values={
            'sips_merchant_id': 'dummy_mid',
            'sips_secret': 'dummy_secret',
        })

        # Override default values
        cls.acquirer = cls.sips
        cls.currency = cls.currency_euro