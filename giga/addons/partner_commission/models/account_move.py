# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from dateutil.relativedelta import relativedelta

from giga import _, fields, models
from giga.tools import formatLang, format_date


class AccountMove(models.Model):
    _inherit = 'account.move'

    referrer_id = fields.Many2one('res.partner', 'Referrer', domain=[('grade_id', '!=', False)], tracking=True)
    commission_po_line_id = fields.Many2one('purchase.order.line', 'Referrer Purchase Order line', copy=False)

    def _get_sales_representative(self):
        self.ensure_one()

        # The subscription's Salesperson should be the Purchase Representative.
        sub = self.invoice_line_ids.mapped('subscription_id')[:1]
        sales_rep = sub and sub.user_id or False

        # No subscription: check the sale order's Salesperson.
        if not sales_rep:
            so = self.invoice_line_ids.mapped('sale_line_ids.order_id')[:1]
            sales_rep = so and so.user_id or False

        return sales_rep

    def _get_commission_purchase_order_domain(self):
        self.ensure_one()

        domain = [
            ('partner_id', '=', self.referrer_id.id),
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'draft'),
            ('currency_id', '=', self.currency_id.id),
            ('purchase_type', '=', 'commission'),
        ]

        sales_rep = self._get_sales_representative()
        if sales_rep:
            domain += [('user_id', '=', sales_rep.id)]

        return domain

    def _get_commission_purchase_order(self):
        self.ensure_one()
        purchase = self.env['purchase.order'].sudo().search(self._get_commission_purchase_order_domain(), limit=1)

        if not purchase:
            sales_rep = self._get_sales_representative()
            purchase = self.env['purchase.order'].with_context(mail_create_nosubscribe=True).sudo().create({
                'partner_id': self.referrer_id.id,
                'currency_id': self.currency_id.id,
                'company_id': self.company_id.id,
                'fiscal_position_id': self.env['account.fiscal.position'].with_company(self.company_id).get_fiscal_position(self.referrer_id.id).id,
                'payment_term_id': self.referrer_id.with_company(self.company_id).property_supplier_payment_term_id.id,
                'user_id': sales_rep and sales_rep.id or False,
                'dest_address_id': self.referrer_id.id,
                'origin': self.name,
                'purchase_type': 'commission',
            })

        return purchase

    def _make_commission(self):
        for move in self.filtered(lambda m: m.move_type in ['out_invoice', 'in_invoice', 'out_refund']):
            if move.move_type in ['out_invoice', 'in_invoice']:
                sign = 1
                if move.commission_po_line_id or not move.referrer_id:
                    continue
            else:
                sign = -1
                if not move.commission_po_line_id:
                    continue

            comm_by_rule = defaultdict(float)

            product = None
            subscription = None
            for line in move.invoice_line_ids:
                rule = line._get_commission_rule()
                if rule:
                    if not product:
                        product = rule.plan_id.product_id
                    if not subscription:
                        subscription = line.subscription_id
                    commission = move.currency_id.round(line.price_subtotal * rule.rate / 100.0)
                    comm_by_rule[rule] += commission

            # regulate commissions
            for r, amount in comm_by_rule.items():
                if r.is_capped:
                    amount = min(amount, r.max_commission)
                    comm_by_rule[r] = amount

            total = sum(comm_by_rule.values())
            if not total:
                continue

            # build description lines
            desc = f"{_('Commission on %s') % (move.name)}, {move.partner_id.name}, {formatLang(self.env, move.amount_untaxed, currency_obj=move.currency_id)}"
            if subscription:
                periods = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months', 'yearly': 'years'}
                date_to = subscription.recurring_next_date
                date_from = fields.Date.subtract(date_to, **{periods[subscription.recurring_rule_type]: subscription.recurring_interval})
                desc += f"\n{subscription.code}, {_('from %s to %s') % (format_date(self.env, date_from), format_date(self.env, date_to))}"

                # extend the description to show the number of months to defer the expense over
                delta = relativedelta(date_to, date_from)
                n_months = delta.years * 12 + delta.months + delta.days // 30
                if n_months:
                    desc += f" ({_('%d month(s)') % (n_months)})"

            purchase = move._get_commission_purchase_order()

            line = self.env['purchase.order.line'].sudo().create({
                'name': desc,
                'product_id': product.id,
                'product_qty': 1,
                'price_unit': total * sign,
                'product_uom': product.uom_id.id,
                'date_planned': fields.Datetime.now(),
                'order_id': purchase.id,
                'qty_received': 1,
            })

            if move.move_type in ['out_invoice', 'in_invoice']:
                # link the purchase order line to the invoice
                move.commission_po_line_id = line
                msg_body = 'New commission. Invoice: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>. Amount: %s.' % (move.id, move.name, formatLang(self.env, total, currency_obj=move.currency_id))
            else:
                msg_body = 'Commission refunded. Invoice: <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>. Amount: %s.' % (move.id, move.name, formatLang(self.env, total, currency_obj=move.currency_id))
            purchase.message_post(body=msg_body)

    def _refund_commission(self):
        return self._make_commission()

    def _reverse_moves(self, default_values_list=None, cancel=False):
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'referrer_id': move.referrer_id.id,
                'commission_po_line_id': move.commission_po_line_id.id,
            })
        return super(AccountMove, self)._reverse_moves(default_values_list=default_values_list, cancel=cancel)

    def action_invoice_paid(self):
        res = super().action_invoice_paid()
        self.filtered(lambda move: move.move_type == 'out_refund')._make_commission()
        self.filtered(lambda move: move.move_type == 'out_invoice')._make_commission()
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_commission_rule(self):
        self.ensure_one()
        template = self.subscription_id.template_id
        # check whether the product is part of the subscription template
        template_id = template.id if template and self.product_id.product_tmpl_id in template.product_ids else None
        sub_pricelist = self.subscription_id.pricelist_id
        pricelist_id =  sub_pricelist and sub_pricelist.id or self.sale_line_ids.mapped('order_id.pricelist_id')[:1].id

        # a specific commission plan can be set on the subscription, taking predence over the referrer's commission plan
        plan = self.move_id.referrer_id.commission_plan_id
        if self.subscription_id:
            plan = self.subscription_id.commission_plan_id

        if not plan:
            return self.env['commission.rule']

        return plan._match_rules(self.product_id, template_id, pricelist_id)
