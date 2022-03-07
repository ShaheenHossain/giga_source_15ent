# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    documents_hr_contracts_tags = fields.Many2many('documents.tag', 'documents_hr_contracts_tags_table')
