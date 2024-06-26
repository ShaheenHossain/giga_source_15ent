# -*- coding: utf-8 -*-
from giga.tests import tagged
from giga import fields
from giga.addons.account.tests.common import AccountTestInvoicingCommon
from giga.tools import date_utils
from giga.tools.misc import formatLang, format_date

from dateutil.relativedelta import relativedelta
from unittest.mock import patch
from freezegun import freeze_time


@tagged('post_install', '-at_install')
class TestAccountReportsFilters(AccountTestInvoicingCommon):

    def _assert_filter_date(self, filter_date, expected_date_values, previous_options=None):
        ''' Initialize the 'date' key in the report options and then, assert the result matches the expectations.

        :param filter_date:             The filter_date report values.
        :param expected_date_values:    The expected results for the options['date'] as a dict.
        '''
        report = self.env['account.report']
        with patch.object(type(report), 'filter_date', filter_date):
            options = {}
            report._init_filter_date(options, previous_options)

            self.assertDictEqual(options['date'], expected_date_values)

    def _assert_filter_comparison(self, filter_date, filter_comparison, expected_period_values, previous_options=None):
        ''' Initialize the 'date'/'comparison' keys in the report options and then, assert the result matches the
        expectations.

        :param filter_date:             The filter_date report values.
        :param filter_comparison:       The filter_comparison report values.
        :param expected_period_values: The expected results for options['comparison']['periods'] as a list of dicts.
        '''
        report = self.env['account.report']
        with patch.object(type(report), 'filter_date', filter_date), patch.object(type(report), 'filter_comparison', filter_comparison):
            options = {}
            report._init_filter_date(options)
            report._init_filter_comparison(options, previous_options)

            self.assertEqual(len(options['comparison']['periods']), len(expected_period_values))

            for i, expected_values in enumerate(expected_period_values):
                self.assertDictEqual(options['comparison']['periods'][i], expected_values)

    ####################################################
    # DATES RANGE
    ####################################################

    @freeze_time('2017-12-31')
    def test_filter_date_month_range(self):
        ''' Test the filter_date with 'this_month'/'last_month' in 'range' mode.'''
        self._assert_filter_date(
            {'filter': 'this_month', 'mode': 'range'},
            {
                'string': 'Dec 2017',
                'period_type': 'month',
                'mode': 'range',
                'filter': 'this_month',
                'date_from': '2017-12-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_date(
            {'filter': 'last_month', 'mode': 'range'},
            {
                'string': 'Nov 2017',
                'period_type': 'month',
                'mode': 'range',
                'filter': 'last_month',
                'date_from': '2017-11-01',
                'date_to': '2017-11-30',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'this_month', 'mode': 'range'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'Nov 2017',
                    'period_type': 'month',
                    'mode': 'range',
                    'date_from': '2017-11-01',
                    'date_to': '2017-11-30',
                    'strict_range': False,
                },
                {
                    'string': 'Oct 2017',
                    'period_type': 'month',
                    'mode': 'range',
                    'date_from': '2017-10-01',
                    'date_to': '2017-10-31',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_month', 'mode': 'range'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'Dec 2016',
                    'period_type': 'month',
                    'mode': 'range',
                    'date_from': '2016-12-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': 'Dec 2015',
                    'period_type': 'month',
                    'mode': 'range',
                    'date_from': '2015-12-01',
                    'date_to': '2015-12-31',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_month', 'mode': 'range'},
            {
                'filter': 'custom',
                'date_from': '2016-12-01',
                'date_to': '2016-12-31',
            },
            [
                {
                    'string': 'Dec 2016',
                    'period_type': 'month',
                    'mode': 'range',
                    'date_from': '2016-12-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_quarter_range(self):
        ''' Test the filter_date with 'this_quarter'/'last_quarter' in 'range' mode.'''
        self._assert_filter_date(
            {'filter': 'this_quarter', 'mode': 'range'},
            {
                'string': 'Q4\N{NO-BREAK SPACE}2017',
                'period_type': 'quarter',
                'mode': 'range',
                'filter': 'this_quarter',
                'date_from': '2017-10-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_date(
            {'filter': 'last_quarter', 'mode': 'range'},
            {
                'string': 'Q3\N{NO-BREAK SPACE}2017',
                'period_type': 'quarter',
                'mode': 'range',
                'filter': 'last_quarter',
                'date_from': '2017-07-01',
                'date_to': '2017-09-30',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'this_quarter', 'mode': 'range'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'Q3\N{NO-BREAK SPACE}2017',
                    'period_type': 'quarter',
                    'mode': 'range',
                    'date_from': '2017-07-01',
                    'date_to': '2017-09-30',
                    'strict_range': False,
                },
                {
                    'string': 'Q2\N{NO-BREAK SPACE}2017',
                    'period_type': 'quarter',
                    'mode': 'range',
                    'date_from': '2017-04-01',
                    'date_to': '2017-06-30',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_quarter', 'mode': 'range'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'Q4\N{NO-BREAK SPACE}2016',
                    'period_type': 'quarter',
                    'mode': 'range',
                    'date_from': '2016-10-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': 'Q4\N{NO-BREAK SPACE}2015',
                    'period_type': 'quarter',
                    'mode': 'range',
                    'date_from': '2015-10-01',
                    'date_to': '2015-12-31',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_quarter', 'mode': 'range'},
            {
                'filter': 'custom',
                'date_from': '2016-10-01',
                'date_to': '2016-12-31'},
            [
                {
                    'string': 'Q4\N{NO-BREAK SPACE}2016',
                    'period_type': 'quarter',
                    'mode': 'range',
                    'date_from': '2016-10-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_fiscalyear_range_full_year(self):
        ''' Test the filter_date with 'this_year'/'last_year' in 'range' mode when the fiscal year ends the 12-31.'''
        self._assert_filter_date(
            {'filter': 'this_year', 'mode': 'range'},
            {
                'string': '2017',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'filter': 'this_year',
                'date_from': '2017-01-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_date(
            {'filter': 'last_year', 'mode': 'range'},
            {
                'string': '2016',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'filter': 'last_year',
                'date_from': '2016-01-01',
                'date_to': '2016-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'range'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': '2016',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2016-01-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': '2015',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2015-01-01',
                    'date_to': '2015-12-31',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'range'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': '2016',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2016-01-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': '2015',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2015-01-01',
                    'date_to': '2015-12-31',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'range'},
            {
                'filter': 'custom',
                'date_from': '2016-01-01',
                'date_to': '2016-12-31'},
            [
                {
                    'string': '2016',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2016-01-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_fiscalyear_range_overlap_years(self):
        ''' Test the filter_date with 'this_year'/'last_year' in 'range' mode when the fiscal year overlaps 2 years.'''
        self.env.company.fiscalyear_last_day = 30
        self.env.company.fiscalyear_last_month = '6'

        self._assert_filter_date(
            {'filter': 'this_year', 'mode': 'range'},
            {
                'string': '2017 - 2018',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'filter': 'this_year',
                'date_from': '2017-07-01',
                'date_to': '2018-06-30',
                'strict_range': False,
            },
        )

        self._assert_filter_date(
            {'filter': 'last_year', 'mode': 'range'},
            {
                'string': '2016 - 2017',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'filter': 'last_year',
                'date_from': '2016-07-01',
                'date_to': '2017-06-30',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'range'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': '2016 - 2017',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2016-07-01',
                    'date_to': '2017-06-30',
                    'strict_range': False,
                },
                {
                    'string': '2015 - 2016',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2015-07-01',
                    'date_to': '2016-06-30',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'range'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': '2016 - 2017',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2016-07-01',
                    'date_to': '2017-06-30',
                    'strict_range': False,
                },
                {
                    'string': '2015 - 2016',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2015-07-01',
                    'date_to': '2016-06-30',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'range'},
            {
                'filter': 'custom',
                'date_from': '2016-07-01',
                'date_to': '2017-06-30',
            },
            [
                {
                    'string': '2016 - 2017',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2016-07-01',
                    'date_to': '2017-06-30',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_fiscalyear_range_custom_years(self):
        ''' Test the filter_date with 'this_year'/'last_year' in 'range' mode with custom account.fiscal.year records.'''
        # Create a custom fiscal year for the nine previous quarters.
        today = fields.Date.from_string('2017-12-31')
        for i in range(9):
            quarter_df, quarter_dt = date_utils.get_quarter(today - relativedelta(months=i * 3))
            self.env['account.fiscal.year'].create({
                'name': 'custom %s' % i,
                'date_from': fields.Date.to_string(quarter_df),
                'date_to': fields.Date.to_string(quarter_dt),
                'company_id': self.env.company.id,
            })

        self._assert_filter_date(
            {'filter': 'this_year', 'mode': 'range'},
            {
                'string': 'custom 0',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'filter': 'this_year',
                'date_from': '2017-10-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_date(
            {'filter': 'last_year', 'mode': 'range'},
            {
                'string': 'custom 1',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'filter': 'last_year',
                'date_from': '2017-07-01',
                'date_to': '2017-09-30',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'range'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'custom 1',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2017-07-01',
                    'date_to': '2017-09-30',
                    'strict_range': False,
                },
                {
                    'string': 'custom 2',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2017-04-01',
                    'date_to': '2017-06-30',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'range'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'custom 4',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2016-10-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': 'custom 8',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2015-10-01',
                    'date_to': '2015-12-31',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'range'},
            {
                'filter': 'custom',
                'date_from': '2017-07-01',
                'date_to': '2017-09-30'},
            [
                {
                    'string': 'custom 1',
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': '2017-07-01',
                    'date_to': '2017-09-30',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_custom_range(self):
        ''' Test the filter_date with a custom dates range.'''
        self._assert_filter_date(
            {
                'filter': 'custom',
                'mode': 'range',
                'date_from': '2017-01-01',
                'date_to': '2017-01-15',
            },
            {
                'string': 'From %s\nto  %s' % (format_date(self.env, '2017-01-01'), format_date(self.env, '2017-01-15')),
                'period_type': 'custom',
                'mode': 'range',
                'filter': 'custom',
                'date_from': '2017-01-01',
                'date_to': '2017-01-15',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {
                'filter': 'custom',
                'mode': 'range',
                'date_from': '2017-01-01',
                'date_to': '2017-01-15',
            },
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'Dec 2016',
                    'period_type': 'month',
                    'mode': 'range',
                    'date_from': '2016-12-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': 'Nov 2016',
                    'period_type': 'month',
                    'mode': 'range',
                    'date_from': '2016-11-01',
                    'date_to': '2016-11-30',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {
                'filter': 'custom',
                'mode': 'range',
                'date_from': '2017-01-01',
                'date_to': '2017-01-15',
            },
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'From %s\nto  %s' % (format_date(self.env, '2016-01-01'), format_date(self.env, '2016-01-15')),
                    'period_type': 'custom',
                    'mode': 'range',
                    'date_from': '2016-01-01',
                    'date_to': '2016-01-15',
                    'strict_range': False,
                },
                {
                    'string': 'From %s\nto  %s' % (format_date(self.env, '2015-01-01'), format_date(self.env, '2015-01-15')),
                    'period_type': 'custom',
                    'mode': 'range',
                    'date_from': '2015-01-01',
                    'date_to': '2015-01-15',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_custom_range_recognition(self):
        ''' Test the period is well recognized when dealing with custom dates range.
        It means date_from = '2018-01-01', date_to = '2018-12-31' must be considered as a full year.
        '''
        self._assert_filter_date(
            {
                'filter': 'custom',
                'mode': 'range',
                'date_from': '2017-12-01',
                'date_to': '2017-12-31',
            },
            {
                'string': 'Dec 2017',
                'period_type': 'month',
                'mode': 'range',
                'filter': 'custom',
                'date_from': '2017-12-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_date(
            {
                'filter': 'custom',
                'mode': 'range',
                'date_from': '2017-10-01',
                'date_to': '2017-12-31',
            },
            {
                'string': 'Q4\N{NO-BREAK SPACE}2017',
                'period_type': 'quarter',
                'mode': 'range',
                'filter': 'custom',
                'date_from': '2017-10-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_date(
            {
                'filter': 'custom',
                'mode': 'range',
                'date_from': '2017-01-01',
                'date_to': '2017-12-31',
            },
            {
                'string': '2017',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'filter': 'custom',
                'date_from': '2017-01-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self.env.company.fiscalyear_last_day = 30
        self.env.company.fiscalyear_last_month = '6'
        self._assert_filter_date(
            {
                'filter': 'custom',
                'mode': 'range',
                'date_from': '2016-07-01',
                'date_to': '2017-06-30',
            },
            {
                'string': '2016 - 2017',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'filter': 'custom',
                'date_from': '2016-07-01',
                'date_to': '2017-06-30',
                'strict_range': False,
            },
        )

        self.env['account.fiscal.year'].create({
            'name': 'custom 0',
            'date_from': '2017-10-01',
            'date_to': '2017-12-31',
            'company_id': self.env.company.id,
        })
        self._assert_filter_date(
            {
                'filter': 'custom',
                'mode': 'range',
                'date_from': '2017-10-01',
                'date_to': '2017-12-31',
            },
            {
                'string': 'custom 0',
                'period_type': 'fiscalyear',
                'mode': 'range',
                'filter': 'custom',
                'date_from': '2017-10-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

    ####################################################
    # SINGLE DATE
    ####################################################

    @freeze_time('2017-12-30')
    def test_filter_date_today_single(self):
        ''' Test the filter_date with 'today' in 'single' mode.'''
        self._assert_filter_date(
            {'filter': 'today', 'mode': 'single'},
            {
                'string': 'As of %s' % format_date(self.env, '2017-12-30'),
                'period_type': 'today',
                'mode': 'single',
                'filter': 'today',
                'date_from': '2017-12-01',
                'date_to': '2017-12-30',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'today', 'mode': 'single'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2017-11-30'),
                    'period_type': 'month',
                    'mode': 'single',
                    'date_from': '2017-11-01',
                    'date_to': '2017-11-30',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2017-10-31'),
                    'period_type': 'month',
                    'mode': 'single',
                    'date_from': '2017-10-01',
                    'date_to': '2017-10-31',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'today', 'mode': 'single'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2016-12-30'),
                    'period_type': 'today',
                    'mode': 'single',
                    'date_from': '2016-12-01',
                    'date_to': '2016-12-30',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2015-12-30'),
                    'period_type': 'today',
                    'mode': 'single',
                    'date_from': '2015-12-01',
                    'date_to': '2015-12-30',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'today', 'mode': 'single'},
            {
                'filter': 'custom',
                'date_to': '2016-12-31',
            },
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2016-12-31'),
                    'period_type': 'custom',
                    'mode': 'single',
                    'date_from': False,
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_month_single(self):
        ''' Test the filter_date with 'this_month'/'last_month' in 'single' mode.'''
        self._assert_filter_date(
            {'filter': 'this_month', 'mode': 'single'},
            {
                'string': 'As of %s' % format_date(self.env, '2017-12-31'),
                'period_type': 'month',
                'mode': 'single',
                'filter': 'this_month',
                'date_from': '2017-12-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'this_month', 'mode': 'single'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2017-11-30'),
                    'period_type': 'month',
                    'mode': 'single',
                    'date_from': '2017-11-01',
                    'date_to': '2017-11-30',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2017-10-31'),
                    'period_type': 'month',
                    'mode': 'single',
                    'date_from': '2017-10-01',
                    'date_to': '2017-10-31',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_month', 'mode': 'single'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2016-12-31'),
                    'period_type': 'month',
                    'mode': 'single',
                    'date_from': '2016-12-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2015-12-31'),
                    'period_type': 'month',
                    'mode': 'single',
                    'date_from': '2015-12-01',
                    'date_to': '2015-12-31',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_quarter_single(self):
        ''' Test the filter_date with 'this_quarter'/'last_quarter' in 'single' mode.'''
        self._assert_filter_date(
            {'filter': 'this_quarter', 'mode': 'single'},
            {
                'string': 'As of %s' % format_date(self.env, '2017-12-31'),
                'period_type': 'quarter',
                'mode': 'single',
                'filter': 'this_quarter',
                'date_from': '2017-10-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'this_quarter', 'mode': 'single'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2017-09-30'),
                    'period_type': 'quarter',
                    'mode': 'single',
                    'date_from': '2017-07-01',
                    'date_to': '2017-09-30',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2017-06-30'),
                    'period_type': 'quarter',
                    'mode': 'single',
                    'date_from': '2017-04-01',
                    'date_to': '2017-06-30',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_quarter', 'mode': 'single'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2016-12-31'),
                    'period_type': 'quarter',
                    'mode': 'single',
                    'date_from': '2016-10-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2015-12-31'),
                    'period_type': 'quarter',
                    'mode': 'single',
                    'date_from': '2015-10-01',
                    'date_to': '2015-12-31',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_fiscalyear_single_full_year(self):
        ''' Test the filter_date with 'this_year'/'last_year' in 'single' mode when the fiscal year ends the 12-31.'''
        self._assert_filter_date(
            {'filter': 'this_year', 'mode': 'single'},
            {
                'string': 'As of %s' % format_date(self.env, '2017-12-31'),
                'period_type': 'fiscalyear',
                'mode': 'single',
                'filter': 'this_year',
                'date_from': '2017-01-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'single'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2016-12-31'),
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2016-01-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2015-12-31'),
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2015-01-01',
                    'date_to': '2015-12-31',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'single'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2016-12-31'),
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2016-01-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2015-12-31'),
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2015-01-01',
                    'date_to': '2015-12-31',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_fiscalyear_single_overlap_years(self):
        ''' Test the filter_date with 'this_year'/'last_year' in 'single' mode when the fiscal year overlaps 2 years.'''
        self.env.company.fiscalyear_last_day = 30
        self.env.company.fiscalyear_last_month = '6'

        self._assert_filter_date(
            {'filter': 'this_year', 'mode': 'single'},
            {
                'string': 'As of %s' % format_date(self.env, '2018-06-30'),
                'period_type': 'fiscalyear',
                'mode': 'single',
                'filter': 'this_year',
                'date_from': '2017-07-01',
                'date_to': '2018-06-30',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'single'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2017-06-30'),
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2016-07-01',
                    'date_to': '2017-06-30',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2016-06-30'),
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2015-07-01',
                    'date_to': '2016-06-30',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'single'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2017-06-30'),
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2016-07-01',
                    'date_to': '2017-06-30',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2016-06-30'),
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2015-07-01',
                    'date_to': '2016-06-30',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_fiscalyear_single_custom_years(self):
        ''' Test the filter_date with 'this_year'/'last_year' in 'single' mode with custom account.fiscal.year records.'''
        # Create a custom fiscal year for the nine previous quarters.
        today = fields.Date.from_string('2017-12-31')
        for i in range(9):
            quarter_df, quarter_dt = date_utils.get_quarter(today - relativedelta(months=i * 3))
            self.env['account.fiscal.year'].create({
                'name': 'custom %s' % i,
                'date_from': fields.Date.to_string(quarter_df),
                'date_to': fields.Date.to_string(quarter_dt),
                'company_id': self.env.company.id,
            })

        self._assert_filter_date(
            {'filter': 'this_year', 'mode': 'single'},
            {
                'string': 'custom 0',
                'period_type': 'fiscalyear',
                'mode': 'single',
                'filter': 'this_year',
                'date_from': '2017-10-01',
                'date_to': '2017-12-31',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'single'},
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'custom 1',
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2017-07-01',
                    'date_to': '2017-09-30',
                    'strict_range': False,
                },
                {
                    'string': 'custom 2',
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2017-04-01',
                    'date_to': '2017-06-30',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {'filter': 'this_year', 'mode': 'single'},
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'custom 4',
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2016-10-01',
                    'date_to': '2016-12-31',
                    'strict_range': False,
                },
                {
                    'string': 'custom 8',
                    'period_type': 'fiscalyear',
                    'mode': 'single',
                    'date_from': '2015-10-01',
                    'date_to': '2015-12-31',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2017-12-31')
    def test_filter_date_custom_single(self):
        ''' Test the filter_date with a custom date in 'single' mode.'''
        self._assert_filter_date(
            {
                'filter': 'custom',
                'mode': 'single',
                'date_to': '2018-01-15',
            },
            {
                'string': 'As of %s' % format_date(self.env, '2018-01-15'),
                'period_type': 'custom',
                'mode': 'single',
                'filter': 'custom',
                'date_from': '2018-01-01',
                'date_to': '2018-01-15',
                'strict_range': False,
            },
        )

        self._assert_filter_comparison(
            {
                'filter': 'custom',
                'mode': 'single',
                'date_to': '2018-01-15',
            },
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2017-12-31'),
                    'period_type': 'month',
                    'mode': 'single',
                    'date_from': '2017-12-01',
                    'date_to': '2017-12-31',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2017-11-30'),
                    'period_type': 'month',
                    'mode': 'single',
                    'date_from': '2017-11-01',
                    'date_to': '2017-11-30',
                    'strict_range': False,
                },
            ],
        )

        self._assert_filter_comparison(
            {
                'filter': 'custom',
                'mode': 'single',
                'date_to': '2018-01-15',
            },
            {'filter': 'same_last_year', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2017-01-15'),
                    'period_type': 'custom',
                    'mode': 'single',
                    'date_from': '2017-01-01',
                    'date_to': '2017-01-15',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2016-01-15'),
                    'period_type': 'custom',
                    'mode': 'single',
                    'date_from': '2016-01-01',
                    'date_to': '2016-01-15',
                    'strict_range': False,
                },
            ],
        )

    @freeze_time('2021-09-01')
    def test_filter_date_custom_single_period_type_month(self):
        ''' Test the filter_date with a custom date in 'single' mode.'''
        self._assert_filter_date(
            {
                'filter': 'custom',
                'mode': 'single',
                'date_to': '2019-07-18',
            },
            {
                'string': 'As of %s' % format_date(self.env, '2019-07-18'),
                'period_type': 'custom',
                'mode': 'single',
                'filter': 'custom',
                'date_from': '2019-07-01',
                'date_to': '2019-07-18',
                'strict_range': False,
            },
            previous_options={
                'date': {
                    'period_type': 'today',
                    'mode': 'single',
                    'strict_range': False,
                    'date_from': '2021-09-01',
                    'date_to': '2019-07-18',
                    'filter': 'custom',
                }
            },
        )

        self._assert_filter_comparison(
            {
                'filter': 'custom',
                'mode': 'single',
                'date_to': '2019-07-18',
            },
            {'filter': 'previous_period', 'number_period': 2},
            [
                {
                    'string': 'As of %s' % format_date(self.env, '2019-06-30'),
                    'period_type': 'month',
                    'mode': 'single',
                    'date_from': '2019-06-01',
                    'date_to': '2019-06-30',
                    'strict_range': False,
                },
                {
                    'string': 'As of %s' % format_date(self.env, '2019-05-31'),
                    'period_type': 'month',
                    'mode': 'single',
                    'date_from': '2019-05-01',
                    'date_to': '2019-05-31',
                    'strict_range': False,
                },
            ],
        )
