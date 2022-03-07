# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models

class PlanningRole(models.Model):
    _inherit = 'planning.role'

    product_ids = fields.One2many('product.template', 'planning_role_id', string='Services', domain=[('type', '=', 'service'), ('sale_ok', '=', True)])
