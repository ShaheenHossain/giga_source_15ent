# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models


class IrDefault(models.Model):
    _name = 'ir.default'
    _inherit = ['studio.mixin', 'ir.default']
