# -*- coding:utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from giga import api, fields, models, _
from giga.exceptions import UserError


class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _description = 'Payslip Batches'
    _order = 'date_end desc'

    name = fields.Char(required=True, readonly=True, states={'draft': [('readonly', False)]})
    slip_ids = fields.One2many('hr.payslip', 'payslip_run_id', string='Payslips', readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'New'),
        ('verify', 'Confirmed'),
        ('close', 'Done'),
        ('paid', 'Paid'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft')
    date_start = fields.Date(string='Date From', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_end = fields.Date(string='Date To', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))
    credit_note = fields.Boolean(string='Credit Note', readonly=True,
        states={'draft': [('readonly', False)]},
        help="If its checked, indicates that all payslips generated from here are refund payslips.")
    payslip_count = fields.Integer(compute='_compute_payslip_count')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, required=True,
        default=lambda self: self.env.company)
    country_id = fields.Many2one(
        'res.country', string='Country',
        related='company_id.country_id', readonly=True
    )
    country_code = fields.Char(related='country_id.code', readonly=True)

    def _compute_payslip_count(self):
        for payslip_run in self:
            payslip_run.payslip_count = len(payslip_run.slip_ids)

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_open(self):
        self.write({'state': 'verify'})

    def action_close(self):
        if self._are_payslips_ready():
            self.write({'state' : 'close'})

    def action_paid(self):
        self.mapped('slip_ids').action_payslip_paid()
        self.write({'state': 'paid'})

    def action_validate(self):
        payslip_done_result = self.mapped('slip_ids').filtered(lambda slip: slip.state not in ['draft', 'cancel']).action_payslip_done()
        self.action_close()
        return payslip_done_result

    def action_open_payslips(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.payslip",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.slip_ids.ids]],
            "name": "Payslips",
        }

    @api.ondelete(at_uninstall=False)
    def _unlink_if_draft_or_cancel(self):
        if any(self.filtered(lambda payslip_run: payslip_run.state not in ('draft'))):
            raise UserError(_('You cannot delete a payslip batch which is not draft!'))
        if any(self.mapped('slip_ids').filtered(lambda payslip: payslip.state not in ('draft', 'cancel'))):
            raise UserError(_('You cannot delete a payslip which is not draft or cancelled!'))

    def _are_payslips_ready(self):
        return all(slip.state in ['done', 'cancel'] for slip in self.mapped('slip_ids'))
