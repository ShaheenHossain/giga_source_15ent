# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
from giga.addons.account_reports.tests.common import TestAccountReportsCommon
from giga.tests import tagged
from giga.tests.common import Form

@tagged('post_install_l10n', 'post_install', '-at_install')
class LuxembourgAssetsReportTaxesTest(TestAccountReportsCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref='l10n_lu.lu_2011_chart_1'):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.company_data['company'].write({
            'ecdf_prefix': '1234AB',
            'matr_number': '1111111111111',
            'vat': 'LU12345613',
        })

        cls.tax_17 = cls.env['account.tax'].search([('company_id', '=', cls.company_data['company'].id), ('name', '=', '17-P-G')])
        cls.tax_3 = cls.env['account.tax'].search([('company_id', '=', cls.company_data['company'].id), ('name', '=', '3-P-G')])

        cls.product = cls.env['product.product'].create({'name': 'product_1', 'lst_price': 100.0})
        cls.partner_be = cls.env['res.partner'].create({
            'name': 'Partner BE',
            'country_id': cls.env.ref('base.be').id,
            'vat': 'BE0477472701',
        })

        line_taxes = [{'taxes': []}, {'taxes': [cls.tax_3]}, {'taxes': [cls.tax_3, cls.tax_17]}]
        cls.inv1 = cls._post_invoice(line_taxes)

    def test_asset_no_invoice(self):
        # Test case with no original_move_line_ids on the asset;
        # then no tax is set, and no tax should be reported for the asset
        self.env['account.asset'].create({
            'name': 'test',
            'asset_type': 'purchase',
            'acquisition_date': datetime.today() - relativedelta(days=400),
            'account_depreciation_id': self.company_data['default_account_expense'].id,
            'account_depreciation_expense_id': self.company_data['default_account_assets'].id,
            'journal_id': self.company_data['default_journal_purchase'].id,
            'original_value': 100.00,
        }).validate()
        report = self.env['account.assets.report']
        report, options = self._get_report_and_options(report, datetime.today() - relativedelta(days=365), datetime.today())
        data = report._get_lu_xml_2_0_report_values(options)['forms'][0]['tables'][0]
        self.assertNotIn('504', data[0].keys())
        self.assertNotIn('505', data[0].keys())

    def test_asset_no_tax(self):
        # Test case with an original_move_line_ids on the asset with no tax
        data = self._get_report_data_linked_assets([self.inv1.invoice_line_ids[0]])
        self.assertNotIn('504', data[0].keys())
        self.assertNotIn('505', data[0].keys())

    def test_asset_single_line(self):
        # Basic test case with one original_move_line_ids with one tax on it
        data = self._get_report_data_linked_assets([self.inv1.invoice_line_ids[1]])
        self.assertEqual(1000.0 + 30.0, data[0].get('504', {}).get('value'))
        self.assertEqual(30.0, data[0].get('505', {}).get('value'))

    def test_asset_multiple_lines_and_taxes(self):
        # Basic test case with one original_move_line_ids with one tax on it
        data = self._get_report_data_linked_assets([self.inv1.invoice_line_ids[1], self.inv1.invoice_line_ids[2]])
        self.assertEqual(2000.0 + 60.0 + 170.0, data[0].get('504', {}).get('value'))
        self.assertEqual(60.0 + 170.0, data[0].get('505', {}).get('value'))

    def test_asset_multiple_assets_per_line(self):
        # Test tax computation on assets created with an account with multiple_assets_per_line set
        account = self.env['account.account'].create({
            'name': 'multiple_assets_per_line_test_account',
            'code': '000001',
            'user_type_id': self.env.ref('account.data_account_type_non_current_assets').id,
            'asset_type': 'purchase',
            'multiple_assets_per_line': True,
            'create_asset': "validate",
        })
        move_form = Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.invoice_date = datetime.today() - relativedelta(days=500)
        move_form.partner_id = self.partner_be
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product
            line_form.account_id = account
            line_form.price_unit = 100.00
            line_form.quantity = 10.0
            line_form.tax_ids.clear()
            line_form.tax_ids.add(self.tax_17)
        move = move_form.save()
        move.action_post()
        report = self.env['account.assets.report']
        # Assets must be in a state different from draft in order to be reported
        for asset in move.asset_ids:
            asset.state = 'open'
        report, options = self._get_report_and_options(report, datetime.today() - relativedelta(days=365), datetime.today())
        data = report._get_lu_xml_2_0_report_values(options)['forms'][0]['tables'][0]
        self.assertEqual(len(data), 10)
        for line in data:
            self.assertEqual((1000.0 + 170.0) / 10, line.get('504', {}).get('value'))
            self.assertEqual(170.0 / 10, line.get('505', {}).get('value'))

    @classmethod
    def _get_report_and_options(cls, report, date_from, date_to):
        report = report.with_context(date_from=date_from, date_to=date_to, lang='EN_us')
        options = report._get_options({'date': {'date_from': date_from, 'date_to': date_to, 'filter': 'custom'}})
        return report, options

    @classmethod
    def _get_report_data_linked_assets(cls, invoice_lines):
        asset_form = Form(cls.env['account.asset'].with_context(asset_type='purchase'))
        for line in invoice_lines:
            asset_form.original_move_line_ids.add(line)
        asset_form.account_depreciation_id = cls.company_data['default_account_expense']
        asset_form.account_depreciation_expense_id = cls.company_data['default_account_assets']
        asset_form.journal_id = cls.company_data['default_journal_purchase']
        asset_form = asset_form.save()
        asset_form.validate()
        report = cls.env['account.assets.report']
        report, options = cls._get_report_and_options(report, datetime.today() - relativedelta(days=365), datetime.today())
        data = report._get_lu_xml_2_0_report_values(options)['forms'][0]['tables'][0]
        return data

    @classmethod
    def _post_invoice(cls, lines):
        move_form = Form(cls.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.invoice_date = datetime.today() - relativedelta(days=500)
        move_form.partner_id = cls.partner_be
        for i, move_line in enumerate(lines):
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = cls.product
                line_form.price_unit = 100.00
                line_form.quantity = 10.0
                line_form.sequence = i
                line_form.tax_ids.clear()
                for tax in move_line['taxes']:
                    line_form.tax_ids.add(tax)
        move = move_form.save()
        move.action_post()
        return move
