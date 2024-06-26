# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, _

class Project(models.Model):
    _inherit = 'project.project'

    contracts_count = fields.Integer('# Contracts', compute='_compute_contracts_count')

    @api.depends('analytic_account_id')
    def _compute_contracts_count(self):
        contracts_data = self.env['hr.contract'].read_group([
            ('analytic_account_id', '!=', False),
            ('analytic_account_id', 'in', self.analytic_account_id.ids)
        ], ['analytic_account_id'], ['analytic_account_id'])
        mapped_data = {data['analytic_account_id'][0]: data['analytic_account_id_count'] for data in contracts_data}
        for project in self:
            project.contracts_count = mapped_data.get(project.analytic_account_id.id, 0)

    # -------------------------------------------
    # Actions
    # -------------------------------------------

    def action_open_project_contracts(self):
        contracts = self.env['hr.contract'].search([('analytic_account_id', '!=', False), ('analytic_account_id', 'in', self.analytic_account_id.ids)])
        action = self.env["ir.actions.actions"]._for_xml_id("hr_payroll.action_hr_contract_repository")
        action.update({
            'views': [[False, 'tree'], [False, 'form'], [False, 'kanban']],
            'context': {'default_analytic_account_id': self.analytic_account_id.id},
            'domain': [('id', 'in', contracts.ids)]
        })
        if(len(contracts) == 1):
            action["views"] = [[False, 'form']]
            action["res_id"] = contracts.id
        return action

    # ----------------------------
    #  Project Updates
    # ----------------------------

    def _get_stat_buttons(self):
        buttons = super(Project, self)._get_stat_buttons()
        if self.user_has_groups('hr_payroll.group_hr_payroll_user'):
            buttons.append({
                'icon': 'book',
                'text': _('Contracts'),
                'number': self.contracts_count,
                'action_type': 'object',
                'action': 'action_open_project_contracts',
                'show': self.contracts_count > 0,
                'sequence': 16,
            })
        return buttons
