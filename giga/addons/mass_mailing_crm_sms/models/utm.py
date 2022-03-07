# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    ab_testing_sms_winner_selection = fields.Selection(selection_add=[('crm_lead_count', 'Leads')])
