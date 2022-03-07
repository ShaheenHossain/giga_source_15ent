# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_de_stnr = fields.Char(string="St.-Nr.", help="Steuernummer. Scheme: ??FF0BBBUUUUP, e.g.: 2893081508152 https://de.wikipedia.org/wiki/Steuernummer")
    l10n_de_widnr = fields.Char(string="W-IdNr.", help="Wirtschafts-Identifikationsnummer.")
