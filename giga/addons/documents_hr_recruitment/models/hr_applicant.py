# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models


class HrApplicant(models.Model):
    _name = 'hr.applicant'
    _inherit = ['hr.applicant', 'documents.mixin']

    def _get_document_tags(self):
        return self.company_id.recruitment_tag_ids

    def _get_document_folder(self):
        return self.company_id.recruitment_folder_id

    def _get_document_partner(self):
        return self.partner_id

    def _check_create_documents(self):
        return self.company_id.documents_recruitment_settings and super()._check_create_documents()
