# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, SUPERUSER_ID
from . import models
from . import controllers

def post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if 'is_fsm' in env['project.project']:
        env['project.project'].search([('is_fsm', '=', True)]).write({'allow_forecast': False})
