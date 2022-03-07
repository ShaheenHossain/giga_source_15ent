# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import models, api
from giga.tools.translate import _
from giga.exceptions import UserError


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.ondelete(at_uninstall=True)
    def _unlink_except_created_by_pos(self):
        for statement in self:
            if not statement.company_id._is_accounting_unalterable() or not statement.journal_id.pos_payment_method_ids:
                continue
            if statement.state != 'open':
                raise UserError(_('You cannot modify anything on a bank statement (name: %s) that was created by point of sale operations.') % statement.name)
        return super().unlink()


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.ondelete(at_uninstall=True)
    def _unlink_except_created_by_pos(self):
        for st_line in self:
            statement = st_line.statement_id
            if not statement.company_id._is_accounting_unalterable() or not statement.s.journal_id.pos_payment_method_ids:
                continue
            if statement.state != 'open':
                raise UserError(_('You cannot modify anything on a bank statement (name: %s) that was created by point of sale operations.') % statement.name)
        return super().unlink()
