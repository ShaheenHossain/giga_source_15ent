# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models


class ReportPaperformat(models.Model):
    _name = 'report.paperformat'
    _inherit = ['studio.mixin', 'report.paperformat']
