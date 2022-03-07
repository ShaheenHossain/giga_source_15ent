# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loyalty_points = fields.Float(company_dependent=True, help='The loyalty points the user won as part of a Loyalty Program')
