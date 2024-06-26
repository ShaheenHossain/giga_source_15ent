# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, models, fields, _
from giga.exceptions import ValidationError


class HrContract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    sign_request_ids = fields.Many2many('sign.request', string='Requested Signatures')
    sign_request_count = fields.Integer(compute='_compute_sign_request_count')

    @api.depends('sign_request_ids')
    def _compute_sign_request_count(self):
        for contract in self:
            contract.sign_request_count = len(contract.sign_request_ids)

    @api.ondelete(at_uninstall=False)
    def _unlink_if_sign_request_canceled(self):
        if self.sign_request_ids.filtered(lambda s: s.state != 'canceled'):
            raise ValidationError(_(
                "You can't delete a contract linked to a signed document, archive it instead."))

    def open_sign_requests(self):
        self.ensure_one()
        if len(self.sign_request_ids.ids) == 1:
            return self.sign_request_ids.go_to_document()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Signature Requests',
            'view_mode': 'kanban',
            'res_model': 'sign.request',
            'domain': [('id', 'in', self.sign_request_ids.ids)]
        }
