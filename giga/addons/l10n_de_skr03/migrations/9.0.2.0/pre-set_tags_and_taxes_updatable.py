# -*- coding: utf-8 -*-

import giga

def migrate(cr, version):
    registry = giga.registry(cr.dbname)
    from giga.addons.account.models.chart_template import migrate_set_tags_and_taxes_updatable
    migrate_set_tags_and_taxes_updatable(cr, registry, 'l10n_de_skr03')
