# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, SUPERUSER_ID

from . import models


def post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Do not send push notification for old event tracks
    env['event.track'].search([]).write({
        'push_reminder': False,
        'push_reminder_delay': 0,
    })
