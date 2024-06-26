# -*- coding: utf-8 -*-

from giga import _, api, models
from giga.exceptions import UserError


class AccountTax(models.Model):
    _inherit = 'account.tax'

    def write(self, vals):
        forbidden_fields = set([
            'amount_type', 'amount', 'type_tax_use', 'tax_group_id', 'price_include',
            'include_base_amount', 'is_base_affected',
        ])
        if forbidden_fields & set(vals.keys()):
            tax_ids = self.env['pos.order.line'].sudo().search([
                ('order_id.session_id.state', '!=', 'closed')
            ]).read(['tax_ids'])
            # Flatten the list of taxes, see https://stackoverflow.com/questions/952914
            tax_ids = set([i for sl in [t['tax_ids'] for t in tax_ids] for i in sl])
            if tax_ids & set(self.ids):
                raise UserError(_(
                    'It is forbidden to modify a tax used in a POS order not posted. '
                    'You must close the POS sessions before modifying the tax.'
                ))
        return super(AccountTax, self).write(vals)

    def get_real_tax_amount(self):
        tax_list = []
        for tax in self:
            tax_repartition_lines = tax.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')
            total_factor = sum(tax_repartition_lines.mapped('factor'))
            real_amount = tax.amount * total_factor
            tax_list.append({'id': tax.id, 'amount': real_amount})
        return tax_list
