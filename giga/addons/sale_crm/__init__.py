# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from . import models
from . import wizard

from giga import api, SUPERUSER_ID

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    teams = env['crm.team'].search([('use_opportunities', '=', False)])
    teams.write({'use_opportunities': True})