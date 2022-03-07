# -*- coding: utf-8 -*-
from giga import fields, models


class Certificate(models.Model):
    _inherit = 'l10n_cl.certificate'

    last_rest_token = fields.Char('Last REST Token')
