# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class SriPayment(models.Model):

    _name = "l10n_ec.sri.payment"
    _description = "SRI Payment Method"

    name = fields.Char("Name")
    code = fields.Char("Code")
