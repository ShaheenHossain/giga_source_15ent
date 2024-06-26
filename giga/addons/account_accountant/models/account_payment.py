# -*- coding: utf-8 -*-
from giga import models, fields, _
from giga.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_open_manual_reconciliation_widget(self):
        ''' Open the manual reconciliation widget for the current payment.
        :return: A dictionary representing an action.
        '''
        self.ensure_one()

        if not self.partner_id:
            raise UserError(_("Payments without a customer can't be matched"))

        liquidity_lines, counterpart_lines, writeoff_lines = self._seek_for_lines()

        action_context = {'company_ids': self.company_id.ids, 'partner_ids': self.partner_id.ids}
        if self.partner_type == 'customer':
            action_context.update({'mode': 'customers'})
        elif self.partner_type == 'supplier':
            action_context.update({'mode': 'suppliers'})

        if counterpart_lines:
            action_context.update({'move_line_id': counterpart_lines[0].id})

        return {
            'type': 'ir.actions.client',
            'tag': 'manual_reconciliation_view',
            'context': action_context,
        }
