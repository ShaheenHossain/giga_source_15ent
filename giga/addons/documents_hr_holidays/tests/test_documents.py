# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import base64
from giga.tests.common import tagged, TransactionCase, new_test_user
from dateutil.relativedelta import relativedelta

TEXT = base64.b64encode(bytes("documents_hr", 'utf-8'))


@tagged('post_install', '-at_install', 'test_document_bridge')
class TestCaseDocumentsBridgeHR(TransactionCase):

    def test_leave_document_creation(self):
        documents_user = new_test_user(self.env, login='fgh', groups='base.group_user,documents.group_documents_user')

        folder = self.env['documents.folder'].create({'name': 'Contract folder test'})
        company = self.env.user.company_id
        company.documents_hr_settings = True
        company.documents_hr_folder = folder.id
        partner = self.env['res.partner'].create({
            'name': 'Employee address',
        })
        employee = self.env['hr.employee'].create({
            'name': 'User Employee',
            'user_id': documents_user.id,
            'address_home_id': partner.id,
        })
        leave_type = self.env['hr.leave.type'].create({'name': 'Sick', 'requires_allocation': 'no'})
        leave = self.env['hr.leave'].create({
            'employee_id': employee.id,
            'holiday_status_id': leave_type.id,
            'number_of_days': 1,
        })
        attachment = self.env['ir.attachment'].create({
            'datas': TEXT,
            'name': 'fileText_test.txt',
            'mimetype': 'text/plain',
            'res_model': leave._name,
            'res_id': leave.id,
        })

        document = self.env['documents.document'].search([('attachment_id', '=', attachment.id)])
        self.assertTrue(document.exists(), "There should be a new document created from the attachment")
        self.assertEqual(document.owner_id, documents_user, "The owner_id should be the document user")
        self.assertEqual(document.partner_id, employee.address_home_id, "The partner_id should be the employee's address")
