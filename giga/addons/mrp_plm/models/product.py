# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    version = fields.Integer('Version', default=1, readonly=True, help="The current version of the product.")
    eco_count = fields.Integer('# ECOs',compute='_compute_eco_count')
    eco_ids = fields.One2many('mrp.eco', 'product_tmpl_id', 'ECOs')

    def _compute_eco_count(self):
        for p in self:
            p.eco_count = len(p.eco_ids)
