# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    batch_payment_id = fields.Many2one('account.batch.payment', ondelete='set null', copy=False,
        compute="_compute_batch_payment_id", store=True, readonly=False)
    amount_signed = fields.Monetary(
        currency_field='currency_id', compute='_compute_amount_signed',
        help='Negative value of amount field if payment_type is outbound')
    payment_method_name = fields.Char(related='payment_method_line_id.name')

    @api.depends('state')
    def _compute_batch_payment_id(self):
        for payment in self:
            payment.batch_payment_id = payment.state == 'posted' and payment.batch_payment_id or None

    @api.depends('amount', 'payment_type')
    def _compute_amount_signed(self):
        for payment in self:
            if payment.payment_type == 'outbound':
                payment.amount_signed = -payment.amount
            else:
                payment.amount_signed = payment.amount

    @api.model
    def create_batch_payment(self):
        # We use self[0] to create the batch; the constrains on the model ensure
        # the consistency of the generated data (same journal, same payment method, ...)
        batch = self.env['account.batch.payment'].create({
            'journal_id': self[0].journal_id.id,
            'payment_ids': [(4, payment.id, None) for payment in self],
            'payment_method_id': self[0].payment_method_id.id,
            'batch_type': self[0].payment_type,
        })

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.batch.payment",
            "views": [[False, "form"]],
            "res_id": batch.id,
        }

    def button_open_batch_payment(self):
        ''' Redirect the user to the batch payments containing this payment.
        :return:    An action on account.batch.payment.
        '''
        self.ensure_one()

        return {
            'name': _("Batch Payment"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.batch.payment',
            'context': {'create': False},
            'view_mode': 'form',
            'res_id': self.batch_payment_id.id,
        }
