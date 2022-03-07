# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    onsip_auth_user = fields.Char("OnSIP authorization User", groups="base.group_user")

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['onsip_auth_user']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['onsip_auth_user']
