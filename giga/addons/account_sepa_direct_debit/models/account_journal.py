# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.


from giga import models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _default_inbound_payment_methods(self):
        res = super()._default_inbound_payment_methods()
        return res | self.env.ref('account_sepa_direct_debit.payment_method_sdd')

    def get_journal_dashboard_datas(self):
        """ Overridden from account in order to add on the dashboard the number
        of payments generated by SDD that still must be sent in XML.
        """
        rslt = super(AccountJournal, self).get_journal_dashboard_datas()
        domain = [
            ('payment_method_code','=','sdd'),
            ('state', '=', 'posted'),
            ('is_move_sent', '=', False),
            ('is_matched', '=', False),
            ('journal_id', '=', self.id),
        ]
        rslt['sdd_payments_to_send_number'] = self.env['account.payment'].search_count(domain)
        return rslt

    def open_sdd_payments(self):
        #return action 'Direct debit payments to collect' with context forged
        ctx = self._context.copy()
        ctx.update({'default_journal_id': self.id, 'search_default_journal_id': self.id})
        action = self.env['ir.actions.act_window']._for_xml_id('account_sepa_direct_debit.action_sdd_payments_to_collect')
        action.update({'context': ctx})
        return action
