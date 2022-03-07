# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    wsServer = fields.Char(default='wss://edge.sip.onsip.com', config_parameter='voip.wsServer')
