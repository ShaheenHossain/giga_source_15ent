# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class DepartureReason(models.Model):
    _inherit = "hr.departure.reason"

    reason_code = fields.Integer()

    def _get_default_departure_reasons(self):
        return {
            **super()._get_default_departure_reasons(),
            'freelance': self.env.ref('l10n_be_hr_payroll.departure_freelance', False),
        }
