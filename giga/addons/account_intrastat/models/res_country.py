# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    intrastat = fields.Boolean(string='Intrastat member')
