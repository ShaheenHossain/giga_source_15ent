# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga.api import Environment, SUPERUSER_ID

def uninstall_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env.ref('fleet.fleet_costs_reporting_action').write({'view_mode': 'graph,pivot'})