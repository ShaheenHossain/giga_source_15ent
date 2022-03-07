# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models


class IrActionsServer(models.Model):
    _name = 'ir.actions.server'
    _inherit = ['studio.mixin', 'ir.actions.server']
