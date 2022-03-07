# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
from giga.addons.point_of_sale.controllers.main import PosController
from giga import http
from giga.http import request


class PosCache(PosController):

    @http.route()
    def load_onboarding_data(self):
        super().load_onboarding_data()
        request.env["pos.cache"].refresh_all_caches()
