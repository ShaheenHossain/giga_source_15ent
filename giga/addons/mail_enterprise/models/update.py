# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga import api
from giga.models import AbstractModel
from giga.tools import cloc

class PublisherWarrantyContract(AbstractModel):
    _inherit = "publisher_warranty.contract"

    @api.model
    def _get_message(self):
        msg = super()._get_message()

        ICP = self.env["ir.config_parameter"]
        if ICP.get_param('publisher_warranty.maintenance_disable') is not False:
            return msg

        msg['maintenance'] = {
            "version": cloc.VERSION,
        }
        try:
            c = cloc.Cloc()
            c.count_env(self.env)
            if c.code:
                msg["maintenance"]["modules"] = c.code
            if c.errors:
                msg["maintenance"]["errors"] = list(c.errors.keys())
        except Exception:
            msg["maintenance"]["errors"] = ['cloc/error']
        return msg
