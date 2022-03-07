# -*- encoding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class IotTrigger(models.Model):
    _inherit = 'iot.trigger'

    action = fields.Selection(selection_add=[('pass', 'Pass'),
                               ('fail', 'Fail'),
                               ('measure', 'Take Measure')])
