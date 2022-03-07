# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models
from giga.osv.expression import AND


class CalendarWebsiteAppointmentShare(models.TransientModel):
    _inherit = 'calendar.appointment.share'

    def _domain_appointment_type_ids(self):
        domain = super()._domain_appointment_type_ids()
        return AND([domain, [('is_published', '!=', False)]])
