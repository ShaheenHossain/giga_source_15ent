# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import http
from giga.http import request
from giga.tools import html2plaintext


class HelpdeskClientController(http.Controller):

    @http.route('/mail_plugin/ticket/create', type='json', auth='outlook',
                cors="*")
    def helpdesk_ticket_create(self, partner_id, email_body, email_subject):
        partner = request.env['res.partner'].browse(partner_id).exists()
        if not partner:
            return {'error': 'partner_not_found'}

        record = request.env['helpdesk.ticket'].create({
            'name': html2plaintext(email_subject),
            'partner_id': partner_id,
            'description': email_body,
            'user_id': request.env.uid
        })

        return {'ticket_id': record.id}
