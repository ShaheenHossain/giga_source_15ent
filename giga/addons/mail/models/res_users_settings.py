# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models


class ResUsersSettings(models.Model):
    _name = 'res.users.settings'
    _description = 'User Settings'

    user_id = fields.Many2one('res.users', string="User", required=True, readonly=True, ondelete='cascade')
    is_discuss_sidebar_category_channel_open = fields.Boolean(string="Is discuss sidebar category channel open?", default=True)
    is_discuss_sidebar_category_chat_open = fields.Boolean(string="Is discuss sidebar category chat open?", default=True)

    # RTC
    push_to_talk_key = fields.Char(string="Push-To-Talk shortcut", help="String formatted to represent a key with modifiers following this pattern: shift.ctrl.alt.key, e.g: truthy.1.true.b")
    use_push_to_talk = fields.Boolean(string="Use the push to talk feature", default=False)
    voice_active_duration = fields.Integer(string="Duration of voice activity in ms", help="How long the audio broadcast will remain active after passing the volume threshold")
    volume_settings_ids = fields.One2many('res.users.settings.volumes', 'user_setting_id', string="Volumes of other partners")

    _sql_constraints = [
        ('unique_user_id', 'UNIQUE(user_id)', 'One user should only have one mail user settings.')
    ]

    @api.model
    def _find_or_create_for_user(self, user):
        settings = user.res_users_settings_ids
        if not settings:
            settings = self.create({'user_id': user.id})
        return settings

    def _res_users_settings_format(self):
        self.ensure_one()
        res = self._read_format(fnames=[name for name, field in self._fields.items() if name == 'id' or not field.automatic])[0]
        res.pop('volume_settings_ids')
        res.update({
            'volume_settings': self.volume_settings_ids._read_format(['id', 'user_setting_id', 'partner_id', 'volume']),
        })
        return res

    def set_res_users_settings(self, new_settings):
        self.ensure_one()
        changed_settings = {}
        for setting in new_settings.keys():
            if setting in self._fields and new_settings[setting] != self[setting]:
                changed_settings[setting] = new_settings[setting]
        self.write(changed_settings)
        self.env['bus.bus'].sendone((self._cr.dbname, 'res.partner', self.user_id.partner_id.id), {
            'type': 'res.users_settings_changed',
            'payload': changed_settings,
        })

    def set_volume_setting(self, partner_id, volume):
        self.ensure_one()
        volume_setting = self.env['res.users.settings.volumes'].search([('user_setting_id', '=', self.id), ('partner_id', '=', partner_id)])
        if volume_setting:
            volume_setting.volume = volume
        else:
            volume_setting = self.env['res.users.settings.volumes'].create([{
                'user_setting_id': self.id,
                'partner_id': partner_id,
                'volume': volume,
            }])
        notification = {
            'type': 'res_users_settings_volumes_update',
            'payload': {
                'volumeSettings': [('insert', {
                    'id': volume_setting.id,
                    'volume': volume_setting.volume,
                })],
            }
        }
        self.env['bus.bus'].sendone((self._cr.dbname, 'res.partner', self.user_id.partner_id.id), notification)
