# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    appraisal_survey_template_id = fields.Many2one(
        'survey.survey', related='company_id.appraisal_survey_template_id', domain=[('is_appraisal', '=', True)], readonly=False)
