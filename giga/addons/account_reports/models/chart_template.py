# coding: utf-8
from giga import models, fields


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        res = super(AccountChartTemplate, self)._load(sale_tax_rate, purchase_tax_rate, company)

        # by default, anglo-saxon companies should have totals
        # displayed below sections in their reports
        company.totals_below_sections = company.anglo_saxon_accounting

        #set a default misc journal for the tax closure
        company.account_tax_periodicity_journal_id = company._get_default_misc_journal()

        company.account_tax_periodicity_reminder_day = 7
        # create the recurring entry
        company.with_company(company)._get_and_update_tax_closing_moves(fields.Date.today(), include_domestic=True)
        return res
