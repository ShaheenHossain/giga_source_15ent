# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import logging
from unittest.mock import patch
from giga.addons.account.models.account_payment_method import AccountPaymentMethod
from giga.fields import Command

from giga.addons.payment.tests.utils import PaymentTestUtils

_logger = logging.getLogger(__name__)


class PaymentCommon(PaymentTestUtils):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        Method_get_payment_method_information = AccountPaymentMethod._get_payment_method_information

        def _get_payment_method_information(self):
            res = Method_get_payment_method_information(self)
            res['none'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
            return res

        cls.currency_euro = cls._prepare_currency('EUR')
        cls.currency_usd = cls._prepare_currency('USD')

        cls.country_belgium = cls.env.ref('base.be')
        cls.country_france = cls.env.ref('base.fr')
        cls.europe = cls.env.ref('base.europe')

        cls.group_user = cls.env.ref('base.group_user')
        cls.group_portal = cls.env.ref('base.group_portal')
        cls.group_public = cls.env.ref('base.group_public')

        cls.admin_user = cls.env.ref('base.user_admin')
        cls.internal_user = cls.env['res.users'].create({
            'name': 'Internal User (Test)',
            'login': 'internal',
            'password': 'internal',
            'groups_id': [Command.link(cls.group_user.id)]
        })
        cls.portal_user = cls.env['res.users'].create({
            'name': 'Portal User (Test)',
            'login': 'payment_portal',
            'password': 'payment_portal',
            'groups_id': [Command.link(cls.group_portal.id)]
        })
        cls.public_user = cls.env.ref('base.public_user')

        cls.admin_partner = cls.admin_user.partner_id
        cls.internal_partner = cls.internal_user.partner_id
        cls.portal_partner = cls.portal_user.partner_id
        cls.default_partner = cls.env['res.partner'].create({
            'name': 'Norbert Buyer',
            'lang': 'en_US',
            'email': 'norbert.buyer@example.com',
            'street': 'Huge Street',
            'street2': '2/543',
            'phone': '0032 12 34 56 78',
            'city': 'Sin City',
            'zip': '1000',
            'country_id': cls.country_belgium.id,
        })

        # Create a dummy acquirer to allow basic tests without any specific acquirer implementation
        arch = """
        <form action="dummy" method="post">
            <input type="hidden" name="view_id" t-att-value="viewid"/>
            <input type="hidden" name="user_id" t-att-value="user_id.id"/>
        </form>
        """  # We exploit the default values `viewid` and `user_id` from QWeb's rendering context
        redirect_form = cls.env['ir.ui.view'].create({
            'name': "Dummy Redirect Form",
            'type': 'qweb',
            'arch': arch,
        })

        with patch.object(AccountPaymentMethod, '_get_payment_method_information', _get_payment_method_information):
            cls.env['account.payment.method'].create({
                'name': 'Dummy method',
                'code': 'none',
                'payment_type': 'inbound'
            })
        cls.dummy_acquirer = cls.env['payment.acquirer'].create({
            'name': "Dummy Acquirer",
            'provider': 'none',
            'state': 'test',
            'allow_tokenization': True,
            'redirect_form_view_id': redirect_form.id,
            'journal_id': cls.company_data['default_journal_bank'].id,
        })

        cls.acquirer = cls.dummy_acquirer
        cls.amount = 1111.11
        cls.company = cls.env.company
        cls.currency = cls.currency_euro
        cls.partner = cls.default_partner
        cls.reference = "Test Transaction"

    #=== Utils ===#

    @classmethod
    def _prepare_currency(cls, currency_code):
        currency = cls.env['res.currency'].with_context(active_test=False).search(
            [('name', '=', currency_code.upper())]
        )
        currency.action_unarchive()
        return currency

    @classmethod
    def _prepare_acquirer(cls, provider='none', company=None, update_values=None):
        """ Prepare and return the first acquirer matching the given provider and company.

        If no acquirer is found in the given company, we duplicate the one from the base company.

        All other acquirers belonging to the same company are disabled to avoid any interferences.

        :param str provider: The provider of the acquirer to prepare
        :param recordset company: The company of the acquirer to prepare, as a `res.company` record
        :param dict update_values: The values used to update the acquirer
        :return: The acquirer to prepare, if found
        :rtype: recordset of `payment.acquirer`
        """
        company = company or cls.env.company
        update_values = update_values or {}

        acquirer = cls.env['payment.acquirer'].sudo().search(
            [('provider', '=', provider), ('company_id', '=', company.id)], limit=1
        )
        if not acquirer:
            base_acquirer = cls.env['payment.acquirer'].sudo().search(
                [('provider', '=', provider)], limit=1
            )
            if not base_acquirer:
                _logger.error("no payment.acquirer found for provider %s", provider)
                return cls.env['payment.acquirer']
            else:
                acquirer = base_acquirer.copy({'company_id': company.id})

        acquirer.write(update_values)
        if not acquirer.journal_id:
            acquirer.journal_id = cls.env['account.journal'].search([
                ('company_id', '=', company.id),
                ('type', '=', 'bank')
            ], limit=1)
        acquirer.state = 'test'
        return acquirer

    def create_transaction(self, flow, sudo=True, **values):
        default_values = {
            'amount': self.amount,
            'currency_id': self.currency.id,
            'acquirer_id': self.acquirer.id,
            'reference': self.reference,
            'operation': f'online_{flow}',
            'partner_id': self.partner.id,
        }
        return self.env['payment.transaction'].sudo(sudo).create(dict(default_values, **values))

    def create_token(self, sudo=True, **values):
        default_values = {
            'name': "XXXXXXXXXXXXXXX-2565 (TEST)",
            'acquirer_id': self.acquirer.id,
            'partner_id': self.partner.id,
            'acquirer_ref': "Acquirer Ref (TEST)",
        }
        return self.env['payment.token'].sudo(sudo).create(dict(default_values, **values))

    def _get_tx(self, reference):
        return self.env['payment.transaction'].sudo().search([
            ('reference', '=', reference),
        ])
