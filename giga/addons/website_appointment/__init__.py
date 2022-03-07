# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from . import models
from . import controllers
from . import wizard

from giga import api, SUPERUSER_ID


def _post_init_website_appointment(cr, registry):
    """
    Published appointment type that already exist from the appointment module.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    appointment_type_ids = env['calendar.appointment.type'].search([])
    for appointment_type in appointment_type_ids:
        appointment_type.is_published = True
