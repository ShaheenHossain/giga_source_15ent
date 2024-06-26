# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def set_values(self):
        fsm_projects = self.env['project.project'].sudo().search([('is_fsm', '=', True)])
        fsm_projects.sudo().write({'allow_quotations': self.group_industry_fsm_quotations})
        return super(ResConfigSettings, self).set_values()
