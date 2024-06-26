# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details

from giga import models, api, fields, _


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    @api.model
    def _default_fsm_project_id(self):
        project = self.env['project.project'].search([('is_fsm', '=', True)], limit=1)
        return project

    fsm_project_id = fields.Many2one('project.project', string='FSM Project', domain=[('is_fsm', '=', True)],
    default=_default_fsm_project_id)

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    def _mail_get_message_subtypes(self):
        res = super()._mail_get_message_subtypes()
        if len(self) == 1:
            task_done_subtype = self.env.ref('helpdesk_fsm.mt_team_ticket_task_done')
            if not self.use_fsm and task_done_subtype in res:
                res -= task_done_subtype
        return res

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    use_fsm = fields.Boolean(related='team_id.use_fsm')
    fsm_task_ids = fields.One2many('project.task', 'helpdesk_ticket_id', string='Tasks', help='Tasks generated from this ticket', domain=[('is_fsm', '=', True)], copy=False)
    fsm_task_count = fields.Integer(compute='_compute_fsm_task_count')

    @api.depends('fsm_task_ids')
    def _compute_fsm_task_count(self):
        ticket_groups = self.env['project.task'].read_group([('is_fsm', '=', True), ('helpdesk_ticket_id', '!=', False)], ['id:count_distinct'], ['helpdesk_ticket_id'])
        ticket_count_mapping = dict(map(lambda group: (group['helpdesk_ticket_id'][0], group['helpdesk_ticket_id_count']), ticket_groups))
        for ticket in self:
            ticket.fsm_task_count = ticket_count_mapping.get(ticket.id, 0)

    def action_view_fsm_tasks(self):
        fsm_form_view = self.env.ref('project.view_task_form2')
        fsm_list_view = self.env.ref('industry_fsm.project_task_view_list_fsm')
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'context': {
                'create': False,
            },
        }

        if len(self.fsm_task_ids) == 1:
            action.update(res_id=self.fsm_task_ids[0].id, views=[(fsm_form_view.id, 'form')])
        else:
            action.update(domain=[('id', 'in', self.fsm_task_ids.ids)], views=[(fsm_list_view.id, 'tree'), (fsm_form_view.id, 'form')], name=_('Tasks from Tickets'))
        return action

    def action_generate_fsm_task(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create a Field Service task'),
            'res_model': 'helpdesk.create.fsm.task',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'use_fsm': True,
                'default_helpdesk_ticket_id': self.id,
                'default_user_id': False,
                'default_partner_id': self.partner_id.id if self.partner_id else False,
                'default_name': self.name,
                'default_project_id': self.team_id.fsm_project_id.id,
            }
        }

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    def _mail_get_message_subtypes(self):
        res = super()._mail_get_message_subtypes()
        if len(self) == 1 and self.team_id:
            task_done_subtype = self.env.ref('helpdesk_fsm.mt_ticket_task_done')
            if not self.team_id.use_fsm and task_done_subtype in res:
                res -= task_done_subtype
        return res
