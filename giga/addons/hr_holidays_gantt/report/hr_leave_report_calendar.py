# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, tools

from giga.addons.base.models.res_partner import _tz_get


class LeaveReportCalendar(models.Model):
    _inherit = "hr.leave.report.calendar"

    @api.model
    def gantt_unavailability(self, start_date, end_date, scale, group_bys=None, rows=None):
        return self.env['hr.leave'].gantt_unavailability(start_date, end_date, scale, group_bys, rows)
