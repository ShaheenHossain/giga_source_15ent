# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    sdd_mandate_ids = fields.One2many(comodel_name='sdd.mandate', inverse_name='partner_id',
        help="Every mandate belonging to this partner.")
    sdd_count = fields.Integer(compute='_compute_sdd_count', string="SDD count")

    def _compute_sdd_count(self):
        sdd_data = self.env['sdd.mandate'].read_group(
            domain=[('partner_id', 'in', self.ids)],
            fields=['partner_id'],
            groupby=['partner_id'])
        mapped_data = dict([(m['partner_id'][0], m['partner_id_count']) for m in sdd_data])
        for partner in self:
            partner.sdd_count = mapped_data.get(partner.id, 0)
