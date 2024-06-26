# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def register_as_main_attachment(self, force=True):
        """Add the automatic scanning of attachments when registered as main.
           To avoid double scanning after message_post, we check that the automatic scanning is only made the first time.
        """
        self.ensure_one()
        super(IrAttachment, self).register_as_main_attachment(force=force)

        if self.res_model == 'account.move' and self.env.company.extract_show_ocr_option_selection == 'auto_send':
            related_record = self.env[self.res_model].browse(self.res_id)
            if related_record.is_invoice() and related_record.extract_state == "no_extract_requested":
                related_record.retry_ocr()
