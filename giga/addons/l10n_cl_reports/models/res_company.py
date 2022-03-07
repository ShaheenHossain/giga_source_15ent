# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    l10n_cl_report_tasa_ppm = fields.Float(string="Tasa PPM (%)")
    l10n_cl_report_fpp_value = fields.Float(string="FPP (%)")
