# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _mailing_enabled = True
