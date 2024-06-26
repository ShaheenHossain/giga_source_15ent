# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, models, fields

class DownloadWizard(models.TransientModel):
    _name = "account.batch.download.wizard"
    _description = 'Account Batch download wizard'

    batch_payment_id = fields.Many2one(string='Batch Payment',
                                 comodel_name='account.batch.payment',
                                 readonly=True,
                                 required=True,
                                 help="Batch payment from which the file has been generated.")

    export_file = fields.Binary(string='File', related='batch_payment_id.export_file', readonly=True, help="Generated XML file")
    export_filename = fields.Char(string='File name', related='batch_payment_id.export_filename', readonly=True, help="Name of the generated XML file")