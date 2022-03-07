# -*- coding:utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.


from giga import fields, models


class HrJob(models.Model):
    _inherit = 'hr.job'

    default_contract_id = fields.Many2one('hr.contract', domain="[('company_id', '=', company_id), ('employee_id', '=', False)]", string="Contract Template",
        help="Default contract used when making an offer to an applicant.")
