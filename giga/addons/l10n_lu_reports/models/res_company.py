# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"

    matr_number = fields.Char(string="Matr Number")
    ecdf_prefix = fields.Char(string="eCDF Prefix")

    def _get_countries_allowing_tax_representative(self):
        rslt = super()._get_countries_allowing_tax_representative()
        rslt.add(self.env.ref('base.lu').code)
        return rslt
