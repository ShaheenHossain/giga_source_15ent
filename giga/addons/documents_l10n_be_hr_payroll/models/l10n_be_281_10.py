# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import base64

from giga import api, models


class L10nBe28110(models.Model):
    _inherit = 'l10n_be.281_10'

    @api.depends('company_id.documents_payroll_folder_id', 'company_id.documents_hr_settings')
    def _compute_documents_enabled(self):
        for wizard in self:
            wizard.documents_enabled = self._payroll_documents_enabled(wizard.company_id)

    @api.model
    def _payroll_documents_enabled(self, company):
        return company.documents_payroll_folder_id and company.documents_hr_settings

    def _post_process_files(self, files):
        super()._post_process_files(files)
        self.env['documents.document'].create([{
            'owner_id': employee.user_id.id,
            'datas': base64.encodebytes(data),
            'name': filename,
            'folder_id': employee.company_id.documents_payroll_folder_id.id,
            'res_model': 'hr.payslip',  # Security Restriction to payroll managers
        } for employee, filename, data in files if self._payroll_documents_enabled(employee.company_id)])

    def action_post_in_documents(self):
        self._action_generate_pdf(post_process=True)
