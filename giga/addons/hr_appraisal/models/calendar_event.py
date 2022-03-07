# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, models


class CalendarEvent(models.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'

    @api.model_create_multi
    def create(self, vals_list):
        events = super().create(vals_list)
        for event in events.filtered(lambda e: e.res_model == 'hr.appraisal'):
            appraisal = self.env['hr.appraisal'].browse(event.res_id)
            if appraisal.exists():
                appraisal.sudo().write({
                    'meeting_ids': [(4, event.id)],
                })
        return events
