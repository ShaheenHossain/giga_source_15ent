# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import time
from giga import models, fields, api, _
from giga.tools.misc import formatLang
from giga.exceptions import UserError


class ECSalesReport(models.AbstractModel):
    _inherit = 'account.sales.report'

    def _get_non_generic_country_codes(self, options):
        codes = super(ECSalesReport, self)._get_non_generic_country_codes(options)
        codes.add('BE')
        return codes

    def _get_ec_sale_code_options_data(self, options):
        if self._get_report_country_code(options) != 'BE':
            return super(ECSalesReport, self)._get_ec_sale_code_options_data(options)

        return {
            'goods': {
                'name': 'L (46L)',
                'tax_report_line_ids':
                    self.env.ref('l10n_be.tax_report_line_46L').ids +
                    self.env.ref('l10n_be.tax_report_line_48s46L').ids,
                'code': 'L',
            },
            'triangular': {
                'name': 'T (46T)',
                'tax_report_line_ids':
                    self.env.ref('l10n_be.tax_report_line_46T').ids +
                    self.env.ref('l10n_be.tax_report_line_48s46T').ids,
                'code': 'T',
            },
            'services': {
                'name': 'S (44)',
                'tax_report_line_ids':
                    self.env.ref('l10n_be.tax_report_line_44').ids +
                    self.env.ref('l10n_be.tax_report_line_48s44').ids,
                'code': 'S',
            },
        }

    def _get_columns_name(self, options):
        if self._get_report_country_code(options) != 'BE':
            return super(ECSalesReport, self)._get_columns_name(options)

        return [
            {},
            {'name': _('Country Code')},
            {'name': _('VAT Number')},
            {'name': _('Code')},
            {'name': _('Amount'), 'class': 'number'},
        ]

    def _process_query_result(self, options, query_result):
        if self._get_report_country_code(options) != 'BE':
            return super(ECSalesReport, self)._process_query_result(options, query_result)

        get_file_data = options.get('get_file_data', False)
        seq = amount_sum = p_count = 0
        ec_country_to_check = self.get_ec_country_codes(options)
        lines = []
        for row in query_result:
            if not row['vat']:
                row['vat'] = ''
                p_count += 1

            amt = row['amount'] or 0.0
            if amt:
                seq += 1
                amount_sum += amt

                if not row['vat']:
                    if options.get('get_file_data', False):
                        raise UserError(_('One or more partners has no VAT Number.'))
                    else:
                        options['missing_vat_warning'] = True

                if row['same_country'] or row['partner_country_code'] not in ec_country_to_check:
                    options['unexpected_intrastat_tax_warning'] = True

                for option_code in options['ec_sale_code']:
                    if row['tax_report_line_id'] in option_code['tax_report_line_ids']:
                        name = option_code['name']
                        code = option_code['code']

                vat = row['vat'].replace(' ', '').upper()

                if get_file_data:
                    columns = [vat.replace(' ', '').upper(), code, amt]
                else:
                    columns = [vat[:2], vat[2:], name, amt]

                if not self.env.context.get('no_format', False):
                    currency_id = self.env.company.currency_id
                    columns[3] = formatLang(self.env, columns[3], currency_obj=currency_id)

                lines.append({
                    'id': row['partner_id'] if not get_file_data else False,
                    'caret_options': 'res.partner',
                    'model': 'res.partner',
                    'name': row['partner_name'] if not get_file_data else False,
                    'columns': [{'name': v} for v in columns],
                    'unfoldable': False,
                    'unfolded': False,
                })

        if get_file_data:
            return {'lines': lines, 'clientnbr': str(seq), 'amountsum': round(amount_sum, 2), 'partner_wo_vat': p_count}
        return lines

    @api.model
    def _get_reports_buttons(self, options):
        if self._get_report_country_code(options) != 'BE':
            return super(ECSalesReport, self)._get_reports_buttons(options)

        return super(ECSalesReport, self)._get_reports_buttons(options) + [
            {'name': _('XML'), 'sequence': 3, 'action': 'print_xml', 'file_export_type': _('XML')}
        ]

    def get_xml(self, options):
        if self._get_report_country_code(options) != 'BE':
            return super(ECSalesReport, self).get_xml(options)
        # Check
        company = self.env.company
        company_vat = company.partner_id.vat
        if not company_vat:
            raise UserError(_('No VAT number associated with your company.'))
        default_address = company.partner_id.address_get()
        address = default_address.get('invoice', company.partner_id)
        if not address.email:
            raise UserError(_('No email address associated with the company.'))
        if not address.phone:
            raise UserError(_('No phone associated with the company.'))

        # Generate xml
        post_code = street = city = country = data_clientinfo = ''
        company_vat = company_vat.replace(' ', '').upper()
        issued_by = company_vat[:2]

        seq_declarantnum = self.env['ir.sequence'].next_by_code('declarantnum')
        dnum = company_vat[2:] + seq_declarantnum[-4:]

        addr = company.partner_id.address_get(['invoice'])
        if addr.get('invoice', False):
            ads = self.env['res.partner'].browse([addr['invoice']])[0]
            phone = ads.phone and ads.phone.replace(' ', '') or ''
            email = ads.email or ''
            city = ads.city or ''
            post_code = ads.zip or ''
            if not city:
                city = ''
            if ads.street:
                street = ads.street
            if ads.street2:
                street += ' ' + ads.street2
            if ads.country_id:
                country = ads.country_id.code

        if not country:
            country = company_vat[:2]

        date_from = options['date'].get('date_from')
        date_to = options['date'].get('date_to')

        options['get_file_data'] = True
        xml_data = self.with_context(no_format=True)._get_lines(options)

        ctx_date_from = date_from[5:10]
        ctx_date_to = date_to[5:10]
        month = None
        quarter = None
        if ctx_date_from == '01-01' and ctx_date_to == '03-31':
            quarter = '1'
        elif ctx_date_from == '04-01' and ctx_date_to == '06-30':
            quarter = '2'
        elif ctx_date_from == '07-01' and ctx_date_to == '09-30':
            quarter = '3'
        elif ctx_date_from == '10-01' and ctx_date_to == '12-31':
            quarter = '4'
        elif ctx_date_from != '01-01' or ctx_date_to != '12-31':
            month = date_from[5:7]

        xml_data.update({
            'company_name': company.name,
            'company_vat': company_vat,
            'vatnum': company_vat[2:],
            'sender_date': str(time.strftime('%Y-%m-%d')),
            'street': street,
            'city': city,
            'post_code': post_code,
            'country': country,
            'email': email,
            'phone': phone.replace('/', '').replace('.', '').replace('(', '').replace(')', '').replace(' ', ''),
            'year': date_from[0:4],
            'month': month,
            'quarter': quarter,
            'comments': self._get_report_manager(options).summary or '',
            'issued_by': issued_by,
            'dnum': dnum,
        })

        data_head = """<?xml version="1.0" encoding="ISO-8859-1"?>
<ns2:IntraConsignment xmlns="http://www.minfin.fgov.be/InputCommon" xmlns:ns2="http://www.minfin.fgov.be/IntraConsignment" IntraListingsNbr="1">
""" + self._get_belgian_xml_export_representative_node()
        data_comp_period = '\n\t\t<ns2:Declarant>\n\t\t\t<VATNumber>%(vatnum)s</VATNumber>\n\t\t\t<Name>%(company_name)s</Name>\n\t\t\t<Street>%(street)s</Street>\n\t\t\t<PostCode>%(post_code)s</PostCode>\n\t\t\t<City>%(city)s</City>\n\t\t\t<CountryCode>%(country)s</CountryCode>\n\t\t\t<EmailAddress>%(email)s</EmailAddress>\n\t\t\t<Phone>%(phone)s</Phone>\n\t\t</ns2:Declarant>'
        data_comp_period += '\n\t\t<ns2:Period>\n'
        if month:
            data_comp_period += '\t\t\t<ns2:Month>%(month)s</ns2:Month>\n'
        elif quarter:
            data_comp_period += '\t\t\t<ns2:Quarter>%(quarter)s</ns2:Quarter>\n'
        data_comp_period += '\t\t\t<ns2:Year>%(year)s</ns2:Year>\n\t\t</ns2:Period>'
        data_comp_period %= xml_data

        data_clientinfo = ''
        seq = 0
        for line in xml_data['lines']:
            seq += 1
            vat = line['columns'][0].get('name', False)
            if not vat:
                raise UserError(_('No vat number defined for %s.', line['name']))
            client = {
                'vatnum': vat[2:].replace(' ', '').upper(),
                'vat': vat,
                'country': vat[:2],
                'amount': line['columns'][2].get('name', 0.0),
                'code': line['columns'][1].get('name', ''),
                'seq': seq,
            }
            data_clientinfo += '\n\t\t<ns2:IntraClient SequenceNumber="%(seq)s">\n\t\t\t<ns2:CompanyVATNumber issuedBy="%(country)s">%(vatnum)s</ns2:CompanyVATNumber>\n\t\t\t<ns2:Code>%(code)s</ns2:Code>\n\t\t\t<ns2:Amount>%(amount).2f</ns2:Amount>\n\t\t</ns2:IntraClient>' % (client)

        data_decl = '\n\t<ns2:IntraListing SequenceNumber="1" ClientsNbr="%(clientnbr)s" DeclarantReference="%(dnum)s" AmountSum="%(amountsum).2f">' % (xml_data)

        data_rslt = data_head + data_decl + data_comp_period + data_clientinfo + '\n\t\t</ns2:IntraListing>\n</ns2:IntraConsignment>' % (xml_data)
        return data_rslt.encode('ISO-8859-1')
