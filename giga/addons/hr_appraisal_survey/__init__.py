# -*- encoding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, SUPERUSER_ID, _

from . import models
from . import wizard
from . import controllers

def _setup_survey_template(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    default_template = env['res.company']._get_default_appraisal_survey_template_id()
    env['res.company'].search([]).write({
        'appraisal_survey_template_id': default_template.id,
    })

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    xml_ids = [
        'survey.survey_user_input_rule_survey_manager',
        'survey.survey_user_input_rule_survey_user_read',
        'survey.survey_user_input_rule_survey_user_cw',
        'survey.survey_user_input_line_rule_survey_manager',
        'survey.survey_user_input_line_rule_survey_user_read',
        'survey.survey_user_input_line_rule_survey_user_cw'
    ]
    domain = "('survey_id.is_appraisal', '=', False)"
    for xml_id in xml_ids:
        rule = env.ref(xml_id, raise_if_not_found=False)
        if rule:
            rule.domain_force = rule.domain_force.replace(domain, "(1, '=', 1)")

    action_xml_ids = [
        'survey.action_survey_form',
        'survey.action_survey_question_form',
        'survey.survey_question_answer_action',
        'survey.action_survey_user_input',
        'survey.survey_user_input_line_action'
    ]
    for xml_id in action_xml_ids:
        act_window = env.ref(xml_id, raise_if_not_found=False)
        if act_window and act_window.domain and 'is_appraisal' in act_window.domain:
            if 'is_page' in act_window.domain:
                act_window.domain = [('is_page', '=', False)]
            else:
                act_window.domain = []
