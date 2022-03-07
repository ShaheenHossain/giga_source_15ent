# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models


class Groups(models.Model):
    _name = 'res.groups'
    _inherit = ['studio.mixin', 'res.groups']
