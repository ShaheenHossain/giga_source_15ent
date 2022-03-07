# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from . import models

from giga import api, SUPERUSER_ID


def _validate_existing_work_entry(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['hr.work.entry'].search([])._check_if_error()
