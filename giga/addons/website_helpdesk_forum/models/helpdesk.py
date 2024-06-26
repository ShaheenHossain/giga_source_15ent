# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models, _
from giga.addons.http_routing.models.ir_http import slug
from giga.exceptions import UserError


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    forum_id = fields.Many2one('forum.forum', string='Help Center Forum')
    forum_url = fields.Char(string='Help Center Forum URL', readonly=True, compute='_compute_forum_url')

    def _compute_forum_url(self):
        for team in self:
            if team.forum_id and team.id:
                team.forum_url = '%s/forum/%s' % (team.get_base_url(), slug(team.forum_id))
            else:
                team.forum_url = False

    @api.onchange('use_website_helpdesk_forum')
    def _onchange_use_website_helpdesk_forum(self):
        if self.use_website_helpdesk_forum:
            self.forum_id = self.env.ref('website_forum.forum_help', raise_if_not_found=False)
        if not self.use_website_helpdesk_forum:
            self.forum_id = False

    def _init_column(self, column_name):
        """ Initialize the value of the given column for existing rows.
            Overridden here because we need the forum_id to be set during the installationg of this module
            only on records (teams) that have use_website_helpdesk_forum set as True
        """
        if column_name != "forum_id" or not self.env.ref('website_forum.forum_help', raise_if_not_found=False):
            super(HelpdeskTeam, self)._init_column(column_name)
        else:
            default_value = self.env.ref('website_forum.forum_help').id

            self.env.cr.execute("""
            UPDATE {}
               SET forum_id = %s
             WHERE use_website_helpdesk_forum AND forum_id IS NULL
            """.format(self._table), [default_value])


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    forum_post_id = fields.Many2one('forum.post', string="Forum Post", copy=False)
    use_website_helpdesk_forum = fields.Boolean(related='team_id.use_website_helpdesk_forum', string='Help Center Active', readonly=True)

    def forum_post_new(self):
        self.ensure_one()
        if not self.team_id.forum_id:
            raise UserError(_('Help Center not active for this team.'))
        forum_post = self.env['forum.post'].search([('name', 'ilike', self.name)])
        for post in forum_post:
            if post.name.lower() == self.name.lower():
                self.forum_post_id = post.id
                break

        if not self.forum_post_id:
            self.forum_post_id = self.env['forum.post'].create({
                'name': self.name,
                'forum_id': self.team_id.forum_id.id,
                'content': self.description or '',
            }).id
        self.message_post(body=_('Ticket has been shared on the %s forum.') % (self.forum_post_id.forum_id.name,))
        return self.forum_post_open()

    def forum_post_open(self):
        self.ensure_one()
        if not self.team_id.forum_id:
            raise UserError(_('Help Center not active for this team.'))
        if not self.forum_post_id:
            raise UserError(_('No post associated to this ticket.'))
        return {
            'type': 'ir.actions.act_url',
            'url': '/forum/' + str(self.team_id.forum_id.id) + '/question/' + str(self.forum_post_id.id),
            'target': 'self',
        }
