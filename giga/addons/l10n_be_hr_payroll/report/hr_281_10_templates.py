# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, models


class ReportL10nBeHrPayroll28110(models.AbstractModel):
    _name = 'report.l10n_be_hr_payroll.report_281_10'
    _description = 'Get 281.10 report as PDF.'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids' : docids,
            'doc_model' : self.env['hr.employee'],
            'data' : data,
            'docs' : self.env['hr.employee'].browse(docids),
        }
