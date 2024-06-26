# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_mrp_wo_tablet_timer = fields.Boolean("Timer", implied_group="mrp_workorder.group_mrp_wo_tablet_timer")

    def set_values(self):
        super().set_values()

        if not self.user_has_groups('mrp.group_mrp_manager'):
            return

        self.env.ref('mrp_workorder.test_type_register_byproducts').sudo().write({
            'active': self.group_mrp_byproducts
        })
