# -*- coding: utf-8 -*-

from giga import models, _
from giga.exceptions import RedirectWarning
import re


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def _get_belgian_xml_export_representative_node(self):
        """ The <Representative> node is common to XML exports made for VAT Listing, VAT Intra,
        and tax declaration. It is used in case the company isn't submitting its report directly,
        but through an external accountant.

        :return: The string containing the complete <Representative> node or an empty string,
                 in case no representative has been configured.
        """
        representative = self.env.company.account_representative_id
        if representative:
            vat_no, country_from_vat = self.env['account.generic.tax.report']._split_vat_number_and_country_code(representative.vat or "")
            country = self.env['res.country'].search([('code', '=', country_from_vat)], limit=1)
            phone = representative.phone or representative.mobile
            node_values = {
                'vat': vat_no,
                'name': representative.name,
                'street': "%s %s" % (representative.street or "", representative.street2 or ""),
                'zip': representative.zip,
                'city': representative.city,
                'country_code': (country or representative.country_id).code,
                'email': representative.email,
                # exclude what's not a number
                'phone': phone and re.sub(r'[./()\s]', '', phone),
            }

            missing_fields = [k for k, v in node_values.items() if not v]
            if missing_fields:
                message = _('Some fields required for the export are missing. Please specify them.')
                action = {
                    'name': _("Company : %s", representative.name),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'res.partner',
                    'views': [[False, 'form']],
                    'target': 'new',
                    'res_id': representative.id,
                    'context': {'create': False},
                }
                button_text = _('Specify')
                additional_context = {'required_fields': missing_fields}
                raise RedirectWarning(message, action, button_text, additional_context)

            return """
    <ns2:Representative>
        <RepresentativeID identificationType="NVAT" issuedBy="%(country_code)s">%(vat)s</RepresentativeID>
        <Name>%(name)s</Name>
        <Street>%(street)s</Street>
        <PostCode>%(zip)s</PostCode>
        <City>%(city)s</City>
        <CountryCode>%(country_code)s</CountryCode>
        <EmailAddress>%(email)s</EmailAddress>
        <Phone>%(phone)s</Phone>
    </ns2:Representative>
            """ % node_values

        return ""
