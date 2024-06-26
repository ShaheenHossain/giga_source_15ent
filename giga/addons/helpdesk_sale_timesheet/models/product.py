# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sla_id = fields.Many2one(
        "helpdesk.sla", string="SLA Policy",
        company_dependent=True,
        domain="[('company_id', '=', current_company_id)]")
