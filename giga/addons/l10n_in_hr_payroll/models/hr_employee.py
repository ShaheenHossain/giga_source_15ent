# -*- coding:utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    uan = fields.Char(string='UAN')
    pan = fields.Char(string='PAN')
    esic_number = fields.Char(string='ESIC Number')
