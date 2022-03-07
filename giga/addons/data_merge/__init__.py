# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import giga.modules.db
from . import models
from giga import api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

def post_init(cr, registry):
    # if not registry.has_unaccent: # FIXME: giga/giga#347
    if not giga.modules.db.has_unaccent(cr):
        _logger.warning('pg extension "unaccent" not loaded, deduplication rules of type "accent" will be treated as "exaxt"')

def uninstall_hook(cr, registry):
    """ This method will remove all the server actions used for 'Merge Action' in the contextual menu. """
    env = api.Environment(cr, SUPERUSER_ID, {})
    models_to_clean = env['ir.model'].search([('ref_merge_ir_act_server_id', '!=', False)])
    actions_to_remove = models_to_clean.mapped('ref_merge_ir_act_server_id')
    actions_to_remove.unlink()