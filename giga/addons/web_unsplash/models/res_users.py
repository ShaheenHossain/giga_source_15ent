# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _has_unsplash_key_rights(self):
        self.ensure_one()
        return self.has_group('base.group_erp_manager')