# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_onboarding_winbooks_state = fields.Selection([('not_done', "Not done"), ('just_done', "Just done"), ('done', "Done")], string="State of the onboarding winbooks step", default='not_done')

    @api.model
    def winbooks_import_action(self):
        return self.env["ir.actions.actions"]._for_xml_id("account_winbooks_import.winbooks_import_action")

    def get_account_dashboard_onboarding_steps_states_names(self):
        return super(ResCompany, self).get_account_dashboard_onboarding_steps_states_names() + ['account_onboarding_winbooks_state']
