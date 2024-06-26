# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.


from giga import fields, models



class HrReferralPoints(models.Model):
    _name = 'hr.referral.points'
    _description = 'Points line for referrals'
    _rec_name = 'points'

    applicant_id = fields.Many2one('hr.applicant')
    hr_referral_reward_id = fields.Many2one('hr.referral.reward')
    ref_user_id = fields.Many2one('res.users', required=True, string='User')
    points = fields.Integer('Points')
    stage_id = fields.Many2one('hr.recruitment.stage', 'Stage')
    sequence_stage = fields.Integer('Sequence of stage', related='stage_id.sequence')
    company_id = fields.Many2one('res.company', 'Company', required=True)
