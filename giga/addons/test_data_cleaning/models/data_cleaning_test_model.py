# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, api, fields, _

class DataCleaningTestModel(models.Model):
    _name = 'data_cleaning.test.model'
    _description = 'Tests: Data Cleaning Test Model'

    active = fields.Boolean(default=True)
    name = fields.Char()
    phone = fields.Char()
    note = fields.Text()
    country_id = fields.Many2one('res.country', default=lambda x: x.env.company.country_id.id)
    company_id = fields.Many2one('res.company', default=lambda x: x.env.company.id)
