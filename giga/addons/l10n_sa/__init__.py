# -*- encoding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, SUPERUSER_ID
from . import models


def load_translations(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('l10n_sa.sa_chart_template_standard').process_coa_translations()
