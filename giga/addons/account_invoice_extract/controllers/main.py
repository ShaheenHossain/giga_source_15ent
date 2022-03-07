# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import http
from giga.http import request


class AccountInvoiceExtractController(http.Controller):
    @http.route('/account_invoice_extract/request_done/<int:extract_remote_id>', type='http', auth='public', csrf=False)
    def request_done(self, extract_remote_id):
        """ This webhook is called when the extraction server is done processing a request."""
        move_to_update = request.env['account.move'].sudo().search([('extract_remote_id', '=', extract_remote_id),
                                                                    ('extract_state', 'in', ['waiting_extraction', 'extract_not_ready']),
                                                                    ('state', '=', 'draft')])
        for move in move_to_update:
            move._check_status()
        return 'OK'
