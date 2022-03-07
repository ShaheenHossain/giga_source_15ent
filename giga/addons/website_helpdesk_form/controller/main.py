# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import http
from giga.http import request
from giga.addons.website.controllers import form


class WebsiteForm(form.WebsiteForm):

    def _handle_website_form(self, model_name, **kwargs):
        email = request.params.get('partner_email')
        if email:
            partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'email': email,
                    'name': request.params.get('partner_name', False)
                })
            request.params['partner_id'] = partner.id

        return super(WebsiteForm, self)._handle_website_form(model_name, **kwargs)
