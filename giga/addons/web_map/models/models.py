# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import _, api, models
from lxml.builder import E
from giga.exceptions import UserError


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _get_default_map_view(self):
        view = E.map()

        if 'partner_id' in self._fields:
            view.set('res_partner', 'partner_id')
        else:
            raise UserError(_("You need to set a Contact field on this model to use the Map View"))

        return view
