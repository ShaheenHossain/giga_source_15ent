# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    product_id = fields.Many2one('product.product', string='Product', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", help="Product concerned by the ticket")
    tracking = fields.Selection(related='product_id.tracking')
    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial Number', help="Lot/Serial number concerned by the ticket", domain="[('product_id', '=', product_id)]")

    pickings_count = fields.Integer('Return Orders Count', compute="_compute_pickings_count")
    picking_ids = fields.Many2many('stock.picking', string="Return Orders", copy=False)

    @api.depends('picking_ids')
    def _compute_pickings_count(self):
        for ticket in self:
            ticket.pickings_count = len(ticket.picking_ids)

    def action_view_pickings(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Return Orders'),
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.picking_ids.ids)],
            'context': dict(self._context, create=False, default_company_id=self.company_id.id)
        }
        if self.pickings_count == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.picking_ids.id
            })
        return action
