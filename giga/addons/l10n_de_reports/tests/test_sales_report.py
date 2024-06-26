# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga.addons.account_reports.tests.account_sales_report_common import AccountSalesReportCommon
from giga.tests import tagged
from freezegun import freeze_time


@tagged('post_install_l10n', 'post_install', '-at_install')
class GermanySalesReportTest(AccountSalesReportCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass('l10n_de_skr03.l10n_de_chart_template')

    @classmethod
    def setup_company_data(cls, company_name, chart_template=None, **kwargs):
        res = super().setup_company_data(company_name, chart_template=chart_template, **kwargs)
        res['company'].update({
            'country_id': cls.env.ref('base.de').id,
            'vat': 'DE123456788',
        })
        return res

    @freeze_time('2019-12-31')
    def test_ec_sales_report(self):
        l_tax = self.env['account.tax'].search([
            ('name', '=', 'Steuerfreie innergem. Lieferung (§4 Abs. 1b UStG)'),
            ('company_id', '=', self.company_data['company'].id)
        ])[0]
        t_tax = self.env['account.tax'].search([
            ('name', '=', '0% Umsatzsteuer Dreiecksgeschäft erster Abnehmer'),
            ('company_id', '=', self.company_data['company'].id)
        ])[0]
        s_tax = self.env['account.tax'].search([
            ('name', '=', '0% Umsatzsteuer Lieferung von Mobilfunkgeräten u.a. (§13b)'),
            ('company_id', '=', self.company_data['company'].id)
        ])[0]
        self._create_invoices([
            (self.partner_a, l_tax, 300),
            (self.partner_a, l_tax, 300),
            (self.partner_a, t_tax, 500),
            (self.partner_b, t_tax, 500),
            (self.partner_a, s_tax, 700),
            (self.partner_b, s_tax, 700),
        ])
        report = self.env['account.sales.report']
        options = report._get_options(None)
        self.assertEqual(report._get_report_country_code(options), 'DE', "The country chosen for EC Sales list should be Germany")
        lines = report._get_lines(options)
        self.assertLinesValues(
            lines,
            #   Partner                country code,            VAT Number,              Tax    Amount
            [   0,                     1,                       2,                       3,     4],
            [
                (self.partner_a.name,  self.partner_a.vat[:2],  self.partner_a.vat[2:],  'L',  '600.00 €'),
                (self.partner_a.name,  self.partner_a.vat[:2],  self.partner_a.vat[2:],  'D',  '500.00 €'),
                (self.partner_b.name,  self.partner_b.vat[:2],  self.partner_b.vat[2:],  'D',  '500.00 €'),
                (self.partner_a.name,  self.partner_a.vat[:2],  self.partner_a.vat[2:],  'S',  '700.00 €'),
                (self.partner_b.name,  self.partner_b.vat[:2],  self.partner_b.vat[2:],  'S',  '700.00 €'),
            ],
        )
        self.assertTrue(report._get_zip(options), 'Error creating CSV')
