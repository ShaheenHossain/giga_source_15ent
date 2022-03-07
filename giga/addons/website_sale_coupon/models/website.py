# -*- coding: utf-8 -*-
from giga import models
from giga.http import request


class Website(models.Model):
    _inherit = 'website'

    def sale_reset(self):
        request.session.pop('pending_coupon_code')
        return super().sale_reset()
