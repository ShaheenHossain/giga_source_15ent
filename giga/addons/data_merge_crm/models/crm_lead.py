# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, api, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    # As this model has his own data merge, avoid to enable the generic data_merge on that model.
    _disable_data_merge = True

    def _merge_method(self, destination, source):
        records = destination + source
        opp_ids = records.filtered(lambda opp: opp.probability < 100)
        merge_opp = opp_ids.merge_opportunity(auto_unlink=False)

        return {
            'records_merged': len(opp_ids),
            'log_chatter': False,
            'post_merge': True,
        }

    def _elect_master(self, records):
        return records._sort_by_confidence_level(reverse=True)[0]
