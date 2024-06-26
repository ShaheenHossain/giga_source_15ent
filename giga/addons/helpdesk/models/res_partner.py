# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ticket_count = fields.Integer("Tickets", compute='_compute_ticket_count')
    sla_ids = fields.Many2many(
        'helpdesk.sla', 'helpdesk_sla_res_partner_rel',
        'res_partner_id', 'helpdesk_sla_id', string='SLA Policies')

    def _compute_ticket_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        # group tickets by partner, and account for each partner in self
        groups = self.env['helpdesk.ticket'].read_group(
            [('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id'],
        )
        self.ticket_count = 0
        for group in groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.ticket_count += group['partner_id_count']
                partner = partner.parent_id

    def action_open_helpdesk_ticket(self):
        action = self.env["ir.actions.actions"]._for_xml_id("helpdesk.helpdesk_ticket_action_main_tree")
        action['context'] = {}
        action['domain'] = [('partner_id', 'child_of', self.ids)]
        return action
