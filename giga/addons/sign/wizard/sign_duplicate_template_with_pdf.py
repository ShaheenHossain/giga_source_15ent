# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
import io
import base64

from PyPDF2 import PdfFileReader

from giga import api, models, fields
from giga.exceptions import UserError

class SignDuplicateTemplatePDF(models.TransientModel):
    _name = 'sign.duplicate.template.pdf'
    _description = 'Sign Duplicate Template with new PDF'

    new_pdf = fields.Binary(string="File name", required=True)
    original_template_id = fields.Many2one(
        'sign.template', string="Original File", required=True, ondelete='cascade',
        default=lambda self: self.env.context.get('active_id', None),
    )
    new_template = fields.Char('New Template Name')

    def duplicate_template_with_pdf(self):
        if not self._compare_page_templates(self.original_template_id.datas, self.new_pdf):
            raise UserError("The template has more pages than the current file, it can't be applied.")

        pdf = self.env['ir.attachment'].create({
            'name': self.new_template or self.original_template_id.name,
            'datas': self.new_pdf,
            'type': 'binary'
        })

        new_template = self.original_template_id.copy({
            'attachment_id': pdf.id,
            'active': True,
            'favorited_ids': [(4, self.env.user.id)],
        })

        return new_template.go_to_custom_template()

    @api.model
    def _compare_page_templates(self, original_file, new_file):
        pages_original_file = PdfFileReader(io.BytesIO(base64.b64decode(original_file)), strict=False, overwriteWarnings=False).getNumPages()
        pages_new_file = PdfFileReader(io.BytesIO(base64.b64decode(new_file)), strict=False, overwriteWarnings=False).getNumPages()
        return pages_new_file >= pages_original_file
