# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models


class BaseAutomation(models.Model):
    _name = 'base.automation'
    _inherit = ['studio.mixin', 'base.automation']
