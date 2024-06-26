# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import json
from datetime import datetime
import logging

import markupsafe

from giga import http, fields
from giga.http import request, content_disposition
from giga.addons.web.controllers.main import _serialize_exception
from giga.tools import html_escape

_logger = logging.getLogger(__name__)

class SalemanDashboard(http.Controller):

    @http.route('/sale_subscription_dashboard/fetch_salesmen', type='json', auth='user')
    def fetch_salesmen(self):

        request.cr.execute("""
            SELECT id
            FROM res_users
            WHERE EXISTS (
                SELECT 1
                FROM account_move
                WHERE invoice_user_id = res_users.id
            )
        """)  # we could also use distinct(invoice_user_id) on account_move, but distinct is slower
        sql_results = request.cr.dictfetchall()

        salesman_ids = request.env['res.users'].search_read([('id', 'in', [x['id'] for x in sql_results])], ['id', 'name', 'display_name'], order='name')
        current_salesmen = [x for x in salesman_ids if x['id'] == request.env.user.id]

        sale_subscription_migration_date = request.env['ir.config_parameter'].sudo().get_param(
            'sale_subscription_log.migration_date')
        if sale_subscription_migration_date:
            try:
                datetime.strptime(sale_subscription_migration_date, '%Y-%m-%d').date()
            except ValueError:
                _logger.error("System parameter 'sale_subscription_log.migration_date' does not use "
                              "the correct format (%%YYYY-%%mm-%%dd) : %s. Correct the entry or delete it.",
                              (sale_subscription_migration_date,))
                sale_subscription_migration_date = False

        dates_ranges = request.env['sale.subscription'].get_dates_ranges()

        return {
            'salesman_ids': salesman_ids,
            'default_salesman': [current_salesmen[0]] if current_salesmen else None,
            'currency_id': request.env.company.currency_id.id,
            'migration_date': sale_subscription_migration_date,
            'dates_ranges': dates_ranges,
        }

    @http.route('/sale_subscription_dashboard/get_values_salesmen', type='json', auth='user')
    def get_values_salesman(self, salesman_ids, start_date, end_date):
        return {'salespersons_statistics': request.env['sale.subscription'].get_salespersons_statistics(salesman_ids, start_date, end_date)}

    @http.route('/salesman_subscription_reports', type='http', auth='user', methods=['POST'], csrf=False)
    def get_report(self, body_html, output_format, **kw):
        uid = request.session.uid
        report_obj = request.env['sale.subscription'].with_user(uid)
        report_name = report_obj.get_report_filename()
        try:
            if output_format == 'pdf':
                response = request.make_response(
                    report_obj.get_pdf(markupsafe.Markup(body_html)),
                    headers=[
                        ('Content-Type', report_obj.get_export_mime_type('pdf')),
                        ('Content-Disposition', content_disposition(report_name + '.pdf'))
                    ]
                )
            return response
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': 'Giga Source Server Error',
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
