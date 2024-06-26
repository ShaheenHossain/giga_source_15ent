#-*- coding:utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from pytz import timezone
from giga import api, models, fields, _
from dateutil.relativedelta import relativedelta, MO, SU
from dateutil import rrule
from collections import defaultdict
from datetime import date, timedelta
from giga.tools import float_round, date_utils
from giga.exceptions import UserError
from giga.addons.l10n_be_hr_payroll.models.hr_contract import EMPLOYER_ONSS


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    meal_voucher_count = fields.Integer(
        compute='_compute_work_entry_dependent_benefits')  # Overrides compute method
    private_car_missing_days = fields.Integer(
        string='Days Not Granting Private Car Reimbursement',
        compute='_compute_work_entry_dependent_benefits')
    representation_fees_missing_days = fields.Integer(
        string='Days Not Granting Representation Fees',
        compute='_compute_work_entry_dependent_benefits')
    l10n_be_is_double_pay = fields.Boolean(compute='_compute_l10n_be_is_double_pay')
    l10n_be_max_seizable_amount = fields.Float(compute='_compute_l10n_be_max_seizable_amount')
    l10n_be_max_seizable_warning = fields.Char(compute='_compute_l10n_be_max_seizable_amount')

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids()
        for slip in self:
            if not slip.employee_id or not slip.date_from or not slip.date_to:
                continue
            if slip.struct_id.code == 'CP200WARRANT':
                months = relativedelta(date_utils.add(slip.date_to, days=1), slip.date_from).months
                if slip.employee_id.id in self.env.context.get('commission_real_values', {}):
                    warrant_value = self.env.context['commission_real_values'][slip.employee_id.id]
                else:
                    warrant_value = slip.contract_id.commission_on_target * months
                warrant_type = self.env.ref('l10n_be_hr_payroll.cp200_other_input_warrant')
                lines_to_remove = slip.input_line_ids.filtered(lambda x: x.input_type_id == warrant_type)
                to_remove_vals = [(3, line.id, False) for line in lines_to_remove]
                to_add_vals = [(0, 0, {
                    'amount': warrant_value,
                    'input_type_id': self.env.ref('l10n_be_hr_payroll.cp200_other_input_warrant').id
                })]
                input_line_vals = to_remove_vals + to_add_vals
                slip.update({'input_line_ids': input_line_vals})
            # If a double holiday pay should be recovered
            elif slip.struct_id.code == 'CP200DOUBLE':
                to_recover = slip._get_sum_european_time_off_days()
                if to_recover:
                    slip.write({'input_line_ids': [(0, 0, {
                        'name': _('European Leaves Deduction'),
                        'amount': to_recover,
                        'input_type_id': self.env.ref('l10n_be_hr_payroll.input_double_holiday_european_leave_deduction').id,
                    })]})
        return res

    @api.depends('worked_days_line_ids.number_of_hours', 'worked_days_line_ids.is_paid', 'worked_days_line_ids.is_credit_time')
    def _compute_worked_hours(self):
        super()._compute_worked_hours()
        for payslip in self:
            payslip.sum_worked_hours -= sum([line.number_of_hours for line in payslip.worked_days_line_ids if line.is_credit_time])

    def _compute_work_entry_dependent_benefits(self):
        if self.env.context.get('salary_simulation'):
            for payslip in self:
                payslip.meal_voucher_count = 20
                payslip.private_car_missing_days = 0
                payslip.representation_fees_missing_days = 0
        else:
            all_benefits = self.env['hr.work.entry.type'].get_work_entry_type_benefits()
            work_entries_benefits_rights = self.env['l10n_be.work.entry.daily.benefit.report'].search_read([
                ('employee_id', 'in', self.mapped('employee_id').ids),
                ('day', '<=', max(self.mapped('date_to'))),
                ('day', '>=', min(self.mapped('date_from')))], ['day', 'employee_id', 'benefit_name'])

            # {(calendar, date_from, date_to): resources}
            mapped_resources = defaultdict(lambda: self.env['resource.resource'])
            for payslip in self:
                contract = payslip.contract_id
                calendar = contract.resource_calendar_id if not contract.time_credit else contract.standard_calendar_id
                mapped_resources[(calendar, payslip.date_from, payslip.date_to)] |= contract.employee_id.resource_id
            # {(calendar, date_from, date_to): intervals}}
            mapped_intervals = {}
            for (calendar, date_from, date_to), resources in mapped_resources.items():
                tz = timezone(calendar.tz)
                mapped_intervals[(calendar, date_from, date_to)] = calendar._attendance_intervals_batch(
                    tz.localize(fields.Datetime.to_datetime(date_from)),
                    tz.localize(fields.Datetime.to_datetime(date_to) + timedelta(days=1, seconds=-1)),
                    resources=resources, tz=tz)

            for payslip in self:
                contract = payslip.contract_id
                benefits = dict.fromkeys(all_benefits, 0)
                date_from = max(payslip.date_from, contract.date_start)
                date_to = min(payslip.date_to, contract.date_end or payslip.date_to)
                for work_entries_benefits_right in (
                        work_entries_benefits_right for work_entries_benefits_right in work_entries_benefits_rights
                        if date_from <= work_entries_benefits_right['day'] <= date_to
                        and payslip.employee_id.id == work_entries_benefits_right['employee_id'][0]):
                    if work_entries_benefits_right['benefit_name'] not in benefits:
                        benefits[work_entries_benefits_right['benefit_name']] = 1
                    else:
                        benefits[work_entries_benefits_right['benefit_name']] += 1

                contract = payslip.contract_id
                resource = contract.employee_id.resource_id
                calendar = contract.resource_calendar_id if not contract.time_credit else contract.standard_calendar_id
                intervals = mapped_intervals[(calendar, payslip.date_from, payslip.date_to)][resource.id]

                nb_of_days_to_work = len({dt_from.date(): True for (dt_from, dt_to, attendance) in intervals})
                payslip.private_car_missing_days = nb_of_days_to_work - (benefits['private_car'] if 'private_car' in benefits else 0)
                payslip.representation_fees_missing_days = nb_of_days_to_work - (benefits['representation_fees'] if 'representation_fees' in benefits else 0)
                payslip.meal_voucher_count = benefits['meal_voucher']

    @api.depends('struct_id')
    def _compute_l10n_be_is_double_pay(self):
        for payslip in self:
            payslip.l10n_be_is_double_pay = payslip.struct_id.code == "CP200DOUBLE"

    @api.depends('date_to', 'line_ids.total', 'input_line_ids.code')
    def _compute_l10n_be_max_seizable_amount(self):
        # Source: https://emploi.belgique.be/fr/themes/remuneration/protection-de-la-remuneration/saisie-et-cession-sur-salaires
        all_payslips = self.env['hr.payslip'].search([
            ('employee_id', 'in', self.employee_id.ids),
            ('state', '!=', 'cancel')])
        payslip_values = all_payslips._get_line_values(['NET'])
        for payslip in self:
            if payslip.struct_id.country_id.code != 'BE':
                payslip.l10n_be_max_seizable_amount = 0
                payslip.l10n_be_max_seizable_warning = False
                continue

            rates = self.env['hr.rule.parameter']._get_parameter_from_code('cp200_seizable_percentages', payslip.date_to, raise_if_not_found=False)
            child_increase = self.env['hr.rule.parameter']._get_parameter_from_code('cp200_seizable_amount_child', payslip.date_to, raise_if_not_found=False)
            if not rates or not child_increase:
                payslip.l10n_be_max_seizable_amount = 0
                payslip.l10n_be_max_seizable_warning = False
                continue

            # Note: the ceiling amounts are based on the net revenues
            period_payslips = all_payslips.filtered(
                lambda p: p.employee_id == payslip.employee_id and p.date_from == payslip.date_from and p.date_to == payslip.date_to)
            net_amount = sum([payslip_values['NET'][p.id]['total'] for p in period_payslips])
            seized_amount = sum([period_payslips._get_input_line_amount(code) for code in ['ATTACH_SALARY', 'ASSIG_SALARY', 'CHILD_SUPPORT']])
            net_amount += seized_amount
            # Note: The reduction for dependant children is not applied most of the time because
            #       the process is too complex.
            # To benefit from this increase in the elusive or non-transferable quotas, the worker
            # whose remuneration is subject to seizure or transfer, must declare it using a form,
            # the model of which has been published in the Belgian Official Gazette. of 30 November
            # 2006.
            # He must attach to this form the documents establishing the reality of the
            # charge invoked.
            # Source: Opinion on the indexation of the amounts set in Article 1, paragraph 4, of
            # the Royal Decree of 27 December 2004 implementing Articles 1409, § 1, paragraph 4,
            # and 1409, § 1 bis, paragraph 4 , of the Judicial Code relating to the limitation of
            # seizure when there are dependent children, MB, December 13, 2019.
            dependent_children = payslip.employee_id.l10n_be_dependent_children_attachment
            max_seizable_amount = 0
            for left, right, rate in rates:
                if dependent_children:
                    left += dependent_children * child_increase
                    right += dependent_children * child_increase
                if left <= net_amount:
                    max_seizable_amount += (min(net_amount, right) - left) * rate
            payslip.l10n_be_max_seizable_amount = max_seizable_amount
            if max_seizable_amount and seized_amount > max_seizable_amount:
                payslip.l10n_be_max_seizable_warning = _('The seized amount (%s€) is above the belgian ceilings. Given a global net salary of %s€ for the pay period and %s dependent children, the maximum seizable amount is equal to %s€', round(seized_amount, 2), round(net_amount, 2), round(dependent_children, 2), round(max_seizable_amount, 2))
            else:
                payslip.l10n_be_max_seizable_warning = False

    def _get_worked_day_lines_hours_per_day(self):
        self.ensure_one()
        if self.contract_id.time_credit:
            return self.contract_id.standard_calendar_id.hours_per_day
        return super()._get_worked_day_lines_hours_per_day()

    def _get_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        if self.struct_id.country_id.code != 'BE':
            return super()._get_worked_day_lines_values(domain=domain)
        # If a belgian payslip has half-day attendances/time off, it the worked days lines should
        # be separated
        work_hours = self.contract_id._get_work_hours_split_half(self.date_from, self.date_to, domain=domain)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        for worked_days_data, duration_data in work_hours_ordered:
            duration_type, work_entry_type_id = worked_days_data
            number_of_days, number_of_hours = duration_data
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            attendance_line = {
                'sequence': work_entry_type.sequence,
                'work_entry_type_id': work_entry_type_id,
                'number_of_days': number_of_days,
                'number_of_hours': number_of_hours,
            }
            res.append(attendance_line)
        # If there is a public holiday less than 30 days after the end of the contract
        # this public holiday should be taken into account in the worked days lines
        if self.contract_id.date_end and self.date_from <= self.contract_id.date_end <= self.date_to:
            # If the contract is followed by another one (eg. after an appraisal)
            if self.contract_id.employee_id.contract_ids.filtered(lambda c: c.state in ['open', 'close'] and c.date_start > self.contract_id.date_end):
                return res
            public_holiday_type = self.env.ref('l10n_be_hr_payroll.work_entry_type_bank_holiday')
            public_leaves = self.contract_id.resource_calendar_id.global_leave_ids.filtered(
                lambda l: l.work_entry_type_id == public_holiday_type)
            # If less than 15 days under contract, the public holidays is not reimbursed
            public_leaves = public_leaves.filtered(
                lambda l: (l.date_from.date() - self.employee_id.first_contract_date).days >= 15)
            # If less than 15 days of occupation -> no payment of the time off after contract
            # If less than 1 month of occupation -> payment of the time off occurring within 15 days after contract.
            # Occupation = duration since the start of the contract, from date to date
            public_leaves = public_leaves.filtered(
                lambda l: 0 < (l.date_from.date() - self.contract_id.date_end).days <= (30 if self.employee_id.first_contract_date + relativedelta(months=1) <= self.contract_id.date_end else 15))
            if public_leaves:
                input_type_id = self.env.ref('l10n_be_hr_payroll.cp200_other_input_after_contract_public_holidays').id
                if input_type_id not in self.input_line_ids.mapped('input_type_id').ids:
                    self.write({'input_line_ids': [(0, 0, {
                        'name': _('After Contract Public Holidays'),
                        'amount': 0.0,
                        'input_type_id': self.env.ref('l10n_be_hr_payroll.cp200_other_input_after_contract_public_holidays').id,
                    })]})
        # Handle loss on commissions
        if self._get_last_year_average_variable_revenues():
            we_types_ids = (
                self.env.ref('l10n_be_hr_payroll.work_entry_type_bank_holiday') + self.env.ref('l10n_be_hr_payroll.work_entry_type_small_unemployment')
            ).ids
            # if self.worked_days_line_ids.filtered(lambda wd: wd.code in ['LEAVE205', 'LEAVE500']):
            if any(line_vals['work_entry_type_id'] in we_types_ids for line_vals in res):
                we_type = self.env.ref('l10n_be_hr_payroll.work_entry_type_simple_holiday_pay_variable_salary')
                res.append({
                    'sequence': we_type.sequence,
                    'work_entry_type_id': we_type.id,
                    'number_of_days': 0,
                    'number_of_hours': 0,
                })
        return res

    def _get_last_year_average_variable_revenues(self):
        if not self.contract_id.commission_on_target:
            return 0
        date_from = self.env.context.get('variable_revenue_date_from', self.date_from)
        payslips = self.env['hr.payslip'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', 'in', ['done', 'paid']),
            ('date_from', '>=', date_from + relativedelta(months=-12, day=1)),
            ('date_from', '<=', date_from),
        ], order="date_from asc")
        complete_payslips = payslips.filtered(
            lambda p: not p._get_worked_days_line_number_of_hours('OUT'))
        if not complete_payslips:
            return 0
        total_amount = complete_payslips._get_line_values(['COMMISSION'], compute_sum=True)['COMMISSION']['sum']['total']
        first_contract_date = self.employee_id.first_contract_date
        if not first_contract_date:
            return 0
        # Only complete months count
        if first_contract_date.day != 1:
            start = first_contract_date + relativedelta(day=1, months=1)
        else:
            start = first_contract_date
        end = date_from + relativedelta(day=31, months=-1)
        number_of_month = (end.year - start.year) * 12 + (end.month - start.month) + 1
        number_of_month = min(12, number_of_month)
        return total_amount / number_of_month if number_of_month else 0

    def _get_last_year_average_warrant_revenues(self):
        warrant_payslips = self.env['hr.payslip'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', 'in', ['done', 'paid']),
            ('struct_id.code', '=', 'CP200WARRANT'),
            ('date_from', '>=', self.date_from + relativedelta(months=-12, day=1)),
            ('date_from', '<', self.date_from),
        ], order="date_from asc")
        total_amount = warrant_payslips._get_line_values(['BASIC'], compute_sum=True)['BASIC']['sum']['total']
        first_contract_date = self.employee_id.first_contract_date
        if not first_contract_date:
            return 0
        # Only complete months count
        if first_contract_date.day != 1:
            start = first_contract_date + relativedelta(day=1, months=1)
        else:
            start = first_contract_date
        end = self.date_from + relativedelta(day=31, months=-1)
        number_of_month = (end.year - start.year) * 12 + (end.month - start.month) + 1
        number_of_month = min(12, number_of_month)
        return total_amount / number_of_month if number_of_month else 0

    def _get_credit_time_lines(self):
        lines_vals = self._get_worked_day_lines(domain=[('is_credit_time', '=', True)], check_out_of_contract=False)
        for line_vals in lines_vals:
            line_vals['is_credit_time'] = True
        return lines_vals

    def _get_out_of_contract_calendar(self):
        self.ensure_one()
        if self.contract_id.time_credit:
            return self.contract_id.standard_calendar_id
        return super()._get_out_of_contract_calendar()

    def _get_new_worked_days_lines(self):
        if not self.contract_id.time_credit:
            return super()._get_new_worked_days_lines()
        if self.struct_id.use_worked_day_lines:
            worked_days_line_values = self._get_worked_day_lines(domain=[('is_credit_time', '=', False)])
            for vals in worked_days_line_values:
                vals['is_credit_time'] = False
            credit_time_line_values = self._get_credit_time_lines()
            return [(5, 0, 0)] + [(0, 0, vals) for vals in worked_days_line_values + credit_time_line_values]
        return [(5, False, False)]

    def _get_base_local_dict(self):
        res = super()._get_base_local_dict()
        res.update({
            'compute_ip': compute_ip,
            'compute_ip_deduction': compute_ip_deduction,
            'compute_withholding_taxes': compute_withholding_taxes,
            'compute_employment_bonus_employees': compute_employment_bonus_employees,
            'compute_special_social_cotisations': compute_special_social_cotisations,
            'compute_double_holiday_withholding_taxes': compute_double_holiday_withholding_taxes,
            'compute_thirteen_month_withholding_taxes': compute_thirteen_month_withholding_taxes,
            'compute_withholding_reduction': compute_withholding_reduction,
            'compute_termination_withholding_rate': compute_termination_withholding_rate,
            'compute_impulsion_plan_amount': compute_impulsion_plan_amount,
            'compute_onss_restructuring': compute_onss_restructuring,
            'EMPLOYER_ONSS': EMPLOYER_ONSS,
        })
        return res

    def _compute_number_complete_months_of_work(self, date_from, date_to, contracts):
        invalid_days_by_months = defaultdict(dict)
        for day in rrule.rrule(rrule.DAILY, dtstart=date_from, until=date_to):
            invalid_days_by_months[day.month][day.date()] = True

        for contract in contracts:
            # In case the 1rst/2nd days are saturday/sunday, be kinder on the
            # notion of complete months
            if contract.date_start.day <= 3:
                contract_start = contract.date_start + relativedelta(day=1)
            else:
                contract_start = contract.date_start
            work_days = {int(d) for d in contract.resource_calendar_id._get_global_attendances().mapped('dayofweek')}

            previous_week_start = max(contract_start + relativedelta(weeks=-1, weekday=MO(-1)), date_from)
            next_week_end = min(contract.date_end + relativedelta(weeks=+1, weekday=SU(+1)) if contract.date_end else date.max, date_to)
            days_to_check = rrule.rrule(rrule.DAILY, dtstart=previous_week_start, until=next_week_end)
            for day in days_to_check:
                day = day.date()
                out_of_schedule = True
                if contract_start <= day <= (contract.date_end or date.max):
                    out_of_schedule = False
                elif day.weekday() not in work_days:
                    out_of_schedule = False
                invalid_days_by_months[day.month][day] &= out_of_schedule

        complete_months = [
            month
            for month, days in invalid_days_by_months.items()
            if not any(days.values())
        ]
        return len(complete_months)

    def _compute_presence_prorata(self, date_from, date_to, contracts):
        unpaid_work_entry_types = self.struct_id.unpaid_work_entry_type_ids
        paid_work_entry_types = self.env['hr.work.entry.type'].search([]) - unpaid_work_entry_types
        hours = contracts._get_work_hours(date_from, date_to)
        paid_hours = sum(v for k, v in hours.items() if k in paid_work_entry_types.ids)
        unpaid_hours = sum(v for k, v in hours.items() if k in unpaid_work_entry_types.ids)
        return paid_hours / (paid_hours + unpaid_hours) if paid_hours or unpaid_hours else 0

    def _get_paid_amount_13th_month(self):
        # Counts the number of fully worked month
        # If any day in the month is not covered by the contract dates coverage
        # the entire month is not taken into account for the proratization
        contracts = self.employee_id.contract_ids.filtered(lambda c: c.state not in ['draft', 'cancel'] and c.structure_type_id == self.struct_id.type_id)
        if not contracts or not self.contract_id.first_contract_date:
            return 0.0

        date_from = self.contract_id.first_contract_date
        date_to = self.date_to + relativedelta(day=31)

        basic = self.contract_id._get_contract_wage()

        force_months = self.input_line_ids.filtered(lambda l: l.code == 'MONTHS')
        if force_months:
            n_months = force_months[0].amount
            presence_prorata = 1
        else:
            # 1. Number of months
            n_months = min(12, self._compute_number_complete_months_of_work(date_from, date_to, contracts))
            # 2. Deduct absences
            presence_prorata = self._compute_presence_prorata(date_from, date_to, contracts)

        fixed_salary = basic * n_months / 12 * presence_prorata

        force_avg_variable_revenues = self.input_line_ids.filtered(lambda l: l.code == 'VARIABLE')
        if force_avg_variable_revenues:
            avg_variable_revenues = force_avg_variable_revenues[0].amount
        else:
            avg_variable_revenues = self.with_context(
                variable_revenue_date_from=self.date_from + relativedelta(months=-1)
            )._get_last_year_average_variable_revenues()
        return fixed_salary + avg_variable_revenues

    def _get_paid_amount_warrant(self):
        self.ensure_one()
        warrant_input_type = self.env.ref('l10n_be_hr_payroll.cp200_other_input_warrant')
        return sum(self.input_line_ids.filtered(lambda a: a.input_type_id == warrant_input_type).mapped('amount'))

    def _get_paid_double_holiday(self):
        self.ensure_one()
        contracts = self.employee_id.contract_ids.filtered(lambda c: c.state not in ['draft', 'cancel'] and c.structure_type_id == self.struct_id.type_id)
        if not contracts:
            return 0.0

        basic = self.contract_id._get_contract_wage()
        force_months = self.input_line_ids.filtered(lambda l: l.code == 'MONTHS')
        if force_months or self.contract_id.first_contract_date > date(self.date_from.year - 1, 1, 1):
            year = self.date_from.year - 1
            date_from = date(year, 1, 1)
            date_to = date(year, 12, 31)

            if force_months:
                n_months = force_months[0].amount
                presence_prorata = 1
            else:
                # 1. Number of months
                n_months = self._compute_number_complete_months_of_work(date_from, date_to, contracts)
                # 2. Deduct absences
                presence_prorata = self._compute_presence_prorata(date_from, date_to, contracts)
            fixed_salary = basic * n_months / 12 * presence_prorata
        else:
            fixed_salary = basic

        force_avg_variable_revenues = self.input_line_ids.filtered(lambda l: l.code == 'VARIABLE')
        if force_avg_variable_revenues:
            avg_variable_revenues = force_avg_variable_revenues[0].amount
        else:
            avg_variable_revenues = self.with_context(
                variable_revenue_date_from=self.date_from + relativedelta(months=-1)
            )._get_last_year_average_variable_revenues()
        return fixed_salary + avg_variable_revenues

    def _get_paid_amount(self):
        self.ensure_one()
        belgian_payslip = self.struct_id.country_id.code == "BE"
        if belgian_payslip:
            if self.struct_id.code == 'CP200THIRTEEN':
                return self._get_paid_amount_13th_month()
            if self.struct_id.code == 'CP200WARRANT':
                return self._get_paid_amount_warrant()
            if self.struct_id.code == 'CP200DOUBLE':
                return self._get_paid_double_holiday()
        return super()._get_paid_amount()

    def _is_active_belgian_languages(self):
        active_langs = self.env['res.lang'].with_context(active_test=True).search([]).mapped('code')
        return any(l in active_langs for l in ["fr_BE", "fr_FR", "nl_BE", "nl_NL", "de_BE", "de_DE"])

    def _get_sum_european_time_off_days(self, check=False):
        self.ensure_one()
        two_years_payslips = self.env['hr.payslip'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date_to', '<=', date(self.date_from.year, 12, 31)),
            ('date_from', '>=', date(self.date_from.year - 2, 1, 1)),
            ('state', 'in', ['done', 'paid']),
        ])
        european_time_off_amount = two_years_payslips._get_worked_days_line_amount('LEAVE216')
        already_recovered_amount = two_years_payslips._get_line_values(['EU.LEAVE.DEDUC'], compute_sum=True)['EU.LEAVE.DEDUC']['sum']['total']
        return european_time_off_amount + already_recovered_amount

    def _is_invalid(self):
        invalid = super()._is_invalid()
        if not invalid and self._is_active_belgian_languages():
            country = self.struct_id.country_id
            lang_employee = self.employee_id.sudo().address_home_id.lang
            if country.code == 'BE' and lang_employee not in ["fr_BE", "fr_FR", "nl_BE", "nl_NL", "de_BE", "de_DE"]:
                return _('This document is a translation. This is not a legal document.')
        return invalid

    def _get_negative_net_input_type(self):
        self.ensure_one()
        if self.struct_id.code == 'CP200MONTHLY':
            return self.env.ref('l10n_be_hr_payroll.input_negative_net')
        return super()._get_negative_net_input_type()

    def action_payslip_done(self):
        regular_pay = self.env.ref('l10n_be_hr_payroll.hr_payroll_structure_cp200_employee_salary')
        invalid_payslips = self.filtered(lambda p: p.struct_id == regular_pay and not p.worked_days_line_ids)
        if invalid_payslips:
            raise UserError(_("The regular pay for these employees don't have any worked day lines:\n%s"), '\n'.join(invalid_payslips.mapped('employee_id.name')))
        if self._is_active_belgian_languages():
            bad_language_slips = self.filtered(
                lambda p: p.struct_id.country_id.code == "BE" and p.employee_id.sudo().address_home_id.lang not in ["fr_BE", "fr_FR", "nl_BE", "nl_NL", "de_BE", "de_DE"])
            if bad_language_slips:
                action = self.env['ir.actions.act_window'].\
                    _for_xml_id('l10n_be_hr_payroll.l10n_be_hr_payroll_employee_lang_wizard_action')
                ctx = dict(self.env.context)
                ctx.update({
                    'employee_ids': bad_language_slips.employee_id.ids,
                    'default_slip_ids': self.ids,
                })
                action['context'] = ctx
                return action
        return super().action_payslip_done()

    def _get_pdf_reports(self):
        res = super()._get_pdf_reports()
        report_n = self.env.ref('l10n_be_hr_payroll.action_report_termination_holidays_n')
        report_n1 = self.env.ref('l10n_be_hr_payroll.action_report_termination_holidays_n1')
        for payslip in self:
            if payslip.struct_id.code == 'CP200HOLN1':
                res[report_n1] |= payslip
            elif payslip.struct_id.code == 'CP200HOLN':
                res[report_n] |= payslip
        return res

    def _get_data_files_to_update(self):
        # Note: file order should be maintained
        return super()._get_data_files_to_update() + [(
            'l10n_be_hr_payroll', [
                'data/hr_rule_parameters_data.xml',
                'data/cp200/employee_double_holidays_data.xml',
                'data/cp200/employee_pfi_data.xml',
                'data/cp200/employee_salary_data.xml',
                'data/cp200/employee_termination_fees_data.xml',
                'data/cp200/employee_termination_holidays_N1_data.xml',
                'data/cp200/employee_termination_holidays_N_data.xml',
                'data/cp200/employee_thirteen_month_data.xml',
                'data/cp200/employee_warrant_salary_data.xml',
                'data/student/student_regular_pay_data.xml',
            ])]


def compute_termination_withholding_rate(payslip, categories, worked_days, inputs):
    # See: https://www.securex.eu/lex-go.nsf/vwReferencesByCategory_fr/52DA120D5DCDAE78C12584E000721081?OpenDocument
    def find_rates(x, rates):
        for low, high, rate in rates:
            if low <= x <= high:
                return rate

    if not inputs.ANNUAL_TAXABLE:
        return 0
    annual_taxable = inputs.ANNUAL_TAXABLE.amount

    # Note: Exoneration for children in charge is managed on the salary.rule for the amount
    rates = payslip.rule_parameter('holiday_pay_pp_rates')
    pp_rate = find_rates(annual_taxable, rates)

    # Rate Reduction for children in charge
    children = payslip.dict.employee_id.dependent_children
    children_reduction = payslip.rule_parameter('holiday_pay_pp_rate_reduction')
    if children and annual_taxable <= children_reduction.get(children, children_reduction[5])[1]:
        pp_rate *= (1 - children_reduction.get(children, children_reduction[5])[0] / 100.0)
    return pp_rate

def compute_withholding_taxes(payslip, categories, worked_days, inputs):

    def compute_basic_bareme(value):
        rates = payslip.rule_parameter('basic_bareme_rates')
        rates = [(limit or float('inf'), rate) for limit, rate in rates]  # float('inf') because limit equals None for last level
        rates = sorted(rates)

        basic_bareme = 0
        previous_limit = 0
        for limit, rate in rates:
            basic_bareme += max(min(value, limit) - previous_limit, 0) * rate
            previous_limit = limit
        return float_round(basic_bareme, precision_rounding=0.01)

    def convert_to_month(value):
        return float_round(value / 12.0, precision_rounding=0.01, rounding_method='DOWN')

    employee = payslip.contract_id.employee_id
    # PART 1: Withholding tax amount computation
    withholding_tax_amount = 0.0

    taxable_amount = categories.GROSS  # Base imposable
    # YTI TODO: master: Move this into another rule (like benefit in kind)
    if payslip.contract_id.transport_mode_private_car:
        threshold = payslip.env['hr.rule.parameter']._get_parameter_from_code(
            'pricate_car_taxable_threshold',
            date=payslip.date_to,
            raise_if_not_found=False)
        if threshold is None:
            threshold = 410  # 2020 value
        contract = payslip.contract_id
        private_car_reimbursed_amount = contract.with_context(
            payslip_date=payslip.date_from)._get_private_car_reimbursed_amount(contract.km_home_work)
        if private_car_reimbursed_amount > (threshold / 12):
            taxable_amount += private_car_reimbursed_amount - (threshold / 12)
    lower_bound = taxable_amount - taxable_amount % 15

    # yearly_gross_revenue = Revenu Annuel Brut
    yearly_gross_revenue = lower_bound * 12.0

    # yearly_net_taxable_amount = Revenu Annuel Net Imposable
    if yearly_gross_revenue <= payslip.rule_parameter('yearly_gross_revenue_bound_expense'):
        yearly_net_taxable_revenue = yearly_gross_revenue * (1.0 - 0.3)
    else:
        yearly_net_taxable_revenue = yearly_gross_revenue - payslip.rule_parameter('expense_deduction')

    # BAREME III: Non resident
    if employee.resident_bool:
        basic_bareme = compute_basic_bareme(yearly_net_taxable_revenue)
        withholding_tax_amount = convert_to_month(basic_bareme)
    else:
        # BAREME I: Isolated or spouse with income
        if employee.marital in ['divorced', 'single', 'widower'] or (employee.marital in ['married', 'cohabitant'] and employee.spouse_fiscal_status != 'without_income'):
            basic_bareme = max(compute_basic_bareme(yearly_net_taxable_revenue) - payslip.rule_parameter('deduct_single_with_income'), 0.0)
            withholding_tax_amount = convert_to_month(basic_bareme)

        # BAREME II: spouse without income
        if employee.marital in ['married', 'cohabitant'] and employee.spouse_fiscal_status == 'without_income':
            yearly_net_taxable_revenue_for_spouse = min(yearly_net_taxable_revenue * 0.3, payslip.rule_parameter('max_spouse_income'))
            basic_bareme_1 = compute_basic_bareme(yearly_net_taxable_revenue_for_spouse)
            basic_bareme_2 = compute_basic_bareme(yearly_net_taxable_revenue - yearly_net_taxable_revenue_for_spouse)
            withholding_tax_amount = convert_to_month(max(basic_bareme_1 + basic_bareme_2 - 2 * payslip.rule_parameter('deduct_single_with_income'), 0))

    # Reduction for other family charges
    if (employee.children and employee.dependent_children) or (employee.other_dependent_people and (employee.dependent_seniors or employee.dependent_juniors)):
        if employee.marital in ['divorced', 'single', 'widower'] or (employee.spouse_fiscal_status != 'without_income'):

            # if employee.marital in ['divorced', 'single', 'widower']:
            #     withholding_tax_amount -= payslip.rule_parameter('isolated_deduction')
            if employee.marital in ['divorced', 'single', 'widower'] and employee.dependent_children:
                withholding_tax_amount -= payslip.rule_parameter('disabled_dependent_deduction')
            if employee.disabled:
                withholding_tax_amount -= payslip.rule_parameter('disabled_dependent_deduction')
            if employee.other_dependent_people and employee.dependent_seniors:
                withholding_tax_amount -= payslip.rule_parameter('dependent_senior_deduction') * employee.dependent_seniors
            if employee.other_dependent_people and employee.dependent_juniors:
                withholding_tax_amount -= payslip.rule_parameter('disabled_dependent_deduction') * employee.dependent_juniors
            if employee.marital in ['married', 'cohabitant'] and employee.spouse_fiscal_status == 'low_income':
                withholding_tax_amount -= payslip.rule_parameter('spouse_low_income_deduction')
            if employee.marital in ['married', 'cohabitant'] and employee.spouse_fiscal_status == 'low_pension':
                withholding_tax_amount -= payslip.rule_parameter('spouse_other_income_deduction')
        if employee.marital in ['married', 'cohabitant'] and employee.spouse_fiscal_status == 'without_income':
            if employee.disabled:
                withholding_tax_amount -= payslip.rule_parameter('disabled_dependent_deduction')
            if employee.disabled_spouse_bool:
                withholding_tax_amount -= payslip.rule_parameter('disabled_dependent_deduction')
            if employee.other_dependent_people and employee.dependent_seniors:
                withholding_tax_amount -= payslip.rule_parameter('dependent_senior_deduction') * employee.dependent_seniors
            if employee.other_dependent_people and employee.dependent_juniors:
                withholding_tax_amount -= payslip.rule_parameter('disabled_dependent_deduction') * employee.dependent_juniors

    # Child Allowances
    n_children = employee.dependent_children
    if n_children > 0:
        children_deduction = payslip.rule_parameter('dependent_basic_children_deduction')
        if n_children <= 8:
            withholding_tax_amount -= children_deduction.get(n_children, 0.0)
        if n_children > 8:
            withholding_tax_amount -= children_deduction.get(8, 0.0) + (n_children - 8) * payslip.rule_parameter('dependent_children_deduction')

    if payslip.contract_id.fiscal_voluntarism:
        voluntary_amount = categories.GROSS * payslip.contract_id.fiscal_voluntary_rate / 100
        if voluntary_amount > withholding_tax_amount:
            withholding_tax_amount = voluntary_amount

    return - max(withholding_tax_amount, 0.0)

def compute_special_social_cotisations(payslip, categories, worked_days, inputs):
    employee = payslip.contract_id.employee_id
    wage = categories.BASIC
    result = 0.0
    if not wage:
        return result
    if employee.resident_bool:
        result = 0.0
    elif employee.marital in ['divorced', 'single', 'widower'] or (employee.marital in ['married', 'cohabitant'] and employee.spouse_fiscal_status == 'without_income'):
        if 0.01 <= wage <= 1095.09:
            result = 0.0
        elif 1095.10 <= wage <= 1945.38:
            result = 0.0
        elif 1945.39 <= wage <= 2190.18:
            result = -min((wage - 1945.38) * 0.076, 18.60)
        elif 2190.19 <= wage <= 6038.82:
            result = -min(18.60 + (wage - 2190.18) * 0.011, 60.94)
        else:
            result = -60.94
    elif employee.marital in ['married', 'cohabitant'] and employee.spouse_fiscal_status != 'without_income':
        if 0.01 <= wage <= 1095.09:
            result = 0.0
        elif 1095.10 <= wage <= 1945.38:
            result = -9.30
        elif 1945.39 <= wage <= 2190.18:
            result = -min(max((wage - 1945.38) * 0.076, 9.30), 18.60)
        elif 2190.19 <= wage <= 6038.82:
            result = -min(18.60 + (wage - 2190.18) * 0.011, 51.64)
        else:
            result = -51.64
    return result

def compute_ip(payslip, categories, worked_days, inputs):
    contract = payslip.contract_id
    if not contract.ip:
        return 0.0
    return payslip.dict._get_paid_amount() * contract.ip_wage_rate / 100.0

def compute_ip_deduction(payslip, categories, worked_days, inputs):
    tax_rate = 0.15
    ip_amount = compute_ip(payslip, categories, worked_days, inputs)
    if not ip_amount:
        return 0.0
    ip_deduction_bracket_1 = payslip.rule_parameter('ip_deduction_bracket_1')
    ip_deduction_bracket_2 = payslip.rule_parameter('ip_deduction_bracket_2')
    if 0.0 <= ip_amount <= ip_deduction_bracket_1:
        tax_rate = tax_rate / 2.0
    elif ip_deduction_bracket_1 < ip_amount <= ip_deduction_bracket_2:
        tax_rate = tax_rate * 3.0 / 4.0
    return - min(ip_amount * tax_rate, 11745)

# ref: https://www.socialsecurity.be/employer/instructions/dmfa/fr/latest/instructions/deductions/workers_reductions/workbonus.html
def compute_employment_bonus_employees(payslip, categories, worked_days, inputs):
    bonus_basic_amount = payslip.rule_parameter('work_bonus_basic_amount')
    wage_lower_bound = payslip.rule_parameter('work_bonus_reference_wage_low')
    if not payslip.dict.worked_days_line_ids and not payslip.env.context.get('salary_simulation'):
        return 0

    # S = (W / H) * U
    # W = salaire brut
    # H = le nombre d'heures de travail déclarées avec un code prestations 1, 3, 4, 5 et 20;
    # U = le nombre maximum d'heures de prestations pour le mois concerné dans le régime de travail concerné
    if payslip.env.context.get('salary_simulation'):
        paid_hours = 1
        total_hours = 1
    else:
        worked_days = payslip.dict.worked_days_line_ids.filtered(lambda wd: wd.code not in ['LEAVE300', 'LEAVE301'])
        paid_hours = sum(worked_days.filtered(lambda wd: wd.amount).mapped('number_of_hours'))  # H
        total_hours = sum(worked_days.mapped('number_of_hours'))  # U

    # 1. - Détermination du salaire mensuel de référence (S)
    salary = categories.BRUT * total_hours / paid_hours  # S = (W/H) x U

    # 2. - Détermination du montant de base de la réduction (R)
    if salary <= wage_lower_bound:
        result = bonus_basic_amount
    elif salary <= payslip.rule_parameter('work_bonus_reference_wage_high'):
        coeff = payslip.rule_parameter('work_bonus_coeff')
        result = bonus_basic_amount - (coeff * (salary - wage_lower_bound))
    else:
        result = 0

    # 3. - Détermination du montant de la réduction (P)
    result = result * paid_hours / total_hours  # P = (H/U) x R

    return min(result, -categories.ONSS)

def compute_double_holiday_withholding_taxes(payslip, categories, worked_days, inputs):
    # See: https://www.securex.eu/lex-go.nsf/vwReferencesByCategory_fr/52DA120D5DCDAE78C12584E000721081?OpenDocument
    def find_rates(x, rates):
        for low, high, rate in rates:
            if low <= x <= high:
                return rate / 100.0

    rates = payslip.rule_parameter('holiday_pay_pp_rates')
    children_exoneration = payslip.rule_parameter('holiday_pay_pp_exoneration')
    children_reduction = payslip.rule_parameter('holiday_pay_pp_rate_reduction')

    employee = payslip.contract_id.employee_id

    gross = categories.GROSS

    contract = payslip.dict.contract_id
    monthly_revenue = contract._get_contract_wage()
    # Count ANT in yearly remuneration
    if contract.internet:
        monthly_revenue += 5.0
    if contract.mobile and not contract.internet:
        monthly_revenue += 4.0 + 5.0
    if contract.mobile and contract.internet:
        monthly_revenue += 4.0
    if contract.has_laptop:
        monthly_revenue += 7.0

    yearly_revenue = monthly_revenue * (1 - 0.1307) * 12.0

    if contract.transport_mode_car:
        if 'vehicle_id' in payslip.dict:
            yearly_revenue += payslip.dict.vehicle_id._get_car_atn(date=payslip.dict.date_from) * 12.0
        else:
            yearly_revenue += contract.car_atn * 12.0

    # Exoneration
    children = employee.dependent_children
    if children > 0 and yearly_revenue <= children_exoneration.get(children, children_exoneration[12]):
        yearly_revenue -= children_exoneration.get(children, children_exoneration[12]) - yearly_revenue

    # Reduction
    if children > 0 and yearly_revenue <= children_reduction.get(children, children_reduction[5])[1]:
        withholding_tax_amount = gross * find_rates(yearly_revenue, rates) * (1 - children_reduction.get(children, children_reduction[5])[0] / 100.0)
    else:
        withholding_tax_amount = gross * find_rates(yearly_revenue, rates)
    return - withholding_tax_amount

def compute_thirteen_month_withholding_taxes(payslip, categories, worked_days, inputs):
    # See: https://www.securex.eu/lex-go.nsf/vwReferencesByCategory_fr/52DA120D5DCDAE78C12584E000721081?OpenDocument
    def find_rates(x, rates):
        for low, high, rate in rates:
            if low <= x <= high:
                return rate / 100.0

    rates = payslip.rule_parameter('exceptional_allowances_pp_rates')
    children_exoneration = payslip.rule_parameter('holiday_pay_pp_exoneration')
    children_reduction = payslip.rule_parameter('holiday_pay_pp_rate_reduction')

    employee = payslip.contract_id.employee_id

    gross = categories.GROSS

    contract = payslip.dict.contract_id
    monthly_revenue = contract._get_contract_wage()
    # Count ANT in yearly remuneration
    if contract.internet:
        monthly_revenue += 5.0
    if contract.mobile and not contract.internet:
        monthly_revenue += 4.0 + 5.0
    if contract.mobile and contract.internet:
        monthly_revenue += 4.0
    if contract.has_laptop:
        monthly_revenue += 7.0

    yearly_revenue = monthly_revenue * (1 - 0.1307) * 12.0

    if contract.transport_mode_car:
        if 'vehicle_id' in payslip.dict:
            yearly_revenue += payslip.dict.vehicle_id._get_car_atn(date=payslip.dict.date_from) * 12.0
        else:
            yearly_revenue += contract.car_atn * 12.0

    # Exoneration
    children = employee.dependent_children
    if children > 0 and yearly_revenue <= children_exoneration.get(children, children_exoneration[12]):
        yearly_revenue -= children_exoneration.get(children, children_exoneration[12]) - yearly_revenue

    # Reduction
    if children > 0 and yearly_revenue <= children_reduction.get(children, children_reduction[5])[1]:
        withholding_tax_amount = gross * find_rates(yearly_revenue, rates) * (1 - children_reduction.get(children, children_reduction[5])[0] / 100.0)
    else:
        withholding_tax_amount = gross * find_rates(yearly_revenue, rates)
    return - withholding_tax_amount

def compute_withholding_reduction(payslip, categories, worked_days, inputs):
    if categories.EmpBonus:
        return min(abs(categories.PP), categories.EmpBonus * 0.3314)
    return 0.0

def compute_impulsion_plan_amount(payslip, categories, worked_days, inputs):
    start = payslip.dict.employee_id.first_contract_date
    end = payslip.dict.date_to
    number_of_months = (end.year - start.year) * 12 + (end.month - start.month)
    numerator = sum(wd.number_of_hours for wd in payslip.dict.worked_days_line_ids if wd.amount > 0)
    denominator = 4 * payslip.dict.contract_id.resource_calendar_id.hours_per_week
    coefficient = numerator / denominator
    if payslip.dict.contract_id.l10n_be_impulsion_plan == '25yo':
        if 0 <= number_of_months <= 23:
            theorical_amount = 500.0
        elif 24 <= number_of_months <= 29:
            theorical_amount = 250.0
        elif 30 <= number_of_months <= 35:
            theorical_amount = 125.0
        else:
            theorical_amount = 0
        return min(theorical_amount, theorical_amount * coefficient)
    elif payslip.dict.contract_id.l10n_be_impulsion_plan == '12mo':
        if 0 <= number_of_months <= 11:
            theorical_amount = 500.0
        elif 12 <= number_of_months <= 17:
            theorical_amount = 250.0
        elif 18 <= number_of_months <= 23:
            theorical_amount = 125.0
        else:
            theorical_amount = 0
        return min(theorical_amount, theorical_amount * coefficient)
    else:
        return 0

def compute_onss_restructuring(payslip, categories, worked_days, inputs):
    # Source: https://www.onem.be/fr/documentation/feuille-info/t115

    # 1. Grant condition
    # A worker who has been made redundant following a restructuring benefits from a reduction in his personal contributions under certain conditions:
    # - The engagement must take place during the validity period of the reduction card. The reduction card is valid for 6 months, calculated from date to date, following the termination of the employment contract.
    # - The gross monthly reference salary does not exceed
    # o 3.071.90: if the worker is under 30 years of age at the time of entry into service
    # o 4,504.93: if the worker is at least 30 years old at the time of entry into service
    # 2. Amount of reduction
    # Lump sum reduction of € 133.33 per month (full time - full month) in personal social security contributions.
    # If the worker does not work full time for a full month or if he works part time, this amount is reduced proportionally.

    # So the reduction is:
    # 1. Full-time worker: P = (J / D) x 133.33
    # - Full time with full one month benefits: € 133.33

    # Example the worker entered service on 02/01/2021 and worked the whole month
    # - Full time with incomplete services: P = (J / D) x 133.33
    # Example: the worker entered service on February 15 -> (10/20) x 133.33 = € 66.665
    # P = amount of reduction
    # J = the number of worker's days declared with a benefit code 1, 3, 4, 5 and 20 .;
    # D = the maximum number of days of benefits for the month concerned in the work scheme concerned.

    # 2. Part-time worker: P = (H / U) x 133.33
    # Example: the worker starts 02/01/2021 and works 19 hours a week.
    # (76/152) x 133.33 = € 66.665
    # Example: the worker starts 02/15/2021 and works 19 hours a week.
    # (38/155) x 133.33 = 33.335 €

    # P = amount of reduction
    # H = the number of working hours declared with a service code 1, 3, 4, 5 and 20;
    # U = the number of monthly hours corresponding to D.

    # 3. Duration of this reduction
    # The benefit applies to all periods of occupation that fall within the period that:
    # starts to run on the day you start your first occupation during the validity period of the restructuring reduction card;
    # and which ends on the last day of the second quarter following the start date of this first occupation.
    # 4. Formalities to be completed
    # The employer deducts the lump sum from the normal amount of personal contributions when paying the remuneration.
    # The ONEM communicates to the ONSS the data concerning the identification of the worker and the validity date of the card.

    # 5. Point of attention
    # If the worker also benefits from a reduction in his personal contributions for low wages, the cumulation between this reduction and that for restructuring cannot exceed the total amount of personal contributions due.

    # If this is the case, we must first reduce the restructuring reduction.

    # Example:
    # - personal contributions = 200 €
    # - restructuring reduction = € 133.33
    # - low salary reduction = 100 €

    # The total amount of reductions exceeds the contributions due. We must therefore first reduce the restructuring reduction and then the balance of the low wage reduction.

    employee = payslip.dict.contract_id.employee_id
    first_contract_date = employee.first_contract_date
    birthdate = employee.birthday
    age = relativedelta(first_contract_date, birthdate).years
    if age < 30:
        threshold = payslip.rule_parameter('onss_restructuring_before_30')
    else:
        threshold = payslip.rule_parameter('onss_restructuring_after_30')

    salary = payslip.paid_amount
    if salary > threshold:
        return 0

    amount = payslip.rule_parameter('onss_restructuring_amount')

    paid_hours = sum(payslip.worked_days_line_ids.filtered(lambda wd: wd.amount).mapped('number_of_hours'))
    total_hours = sum(payslip.worked_days_line_ids.mapped('number_of_hours'))
    ratio = paid_hours / total_hours if total_hours else 0

    start = first_contract_date
    end = payslip.dict.date_to
    number_of_months = (end.year - start.year) * 12 + (end.month - start.month)
    if 0 <= number_of_months <= 6:
        return amount * ratio
    return 0
