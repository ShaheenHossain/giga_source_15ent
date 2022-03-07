# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import api, SUPERUSER_ID
from . import models
from . import wizard


def create_check_sequence_on_bank_journals(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.journal'].search([('type', '=', 'bank')])._create_check_sequence()
