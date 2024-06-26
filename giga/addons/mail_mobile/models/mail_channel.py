# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    def _notify_record_by_ocn(self, message, rdata, msg_vals=False, **kwargs):
        """ Specifically handle channel members. """
        icp_sudo = self.env['ir.config_parameter'].sudo()
        # Avoid to send notification if this feature is disabled or if no user use the mobile app.
        if not icp_sudo.get_param('giga_ocn.project_id') or not icp_sudo.get_param('mail_mobile.enable_ocn'):
            return

        chat_channels = self.filtered(lambda channel: channel.channel_type == 'chat')
        if chat_channels:
            # modify rdata only for calling super. Do not deep copy as we only
            # add data into list but we do not modify item content
            channel_rdata = rdata.copy()
            channel_rdata += [
                {'id': partner.id,
                 'share': partner.partner_share,
                 'active': partner.active,
                 'notif': 'ocn',
                 'type': 'customer',
                 'groups': [],
                }
                for partner in chat_channels.mapped("channel_partner_ids")
            ]
        else:
            channel_rdata = rdata

        return super(MailChannel, self)._notify_record_by_ocn(message, channel_rdata, msg_vals=msg_vals, **kwargs)

    def _notify_by_ocn_send_prepare_payload(self, message, receiver_ids, msg_vals=False):
        payload = super(MailChannel, self)._notify_by_ocn_send_prepare_payload(message, receiver_ids, msg_vals=msg_vals)
        payload['action'] = 'mail.action_discuss'
        record_name = msg_vals.get('record_name') if msg_vals else message.record_name
        if self.channel_type == 'chat':
            payload['subject'] = payload['author_name']
            payload['type'] = 'chat'
            payload['android_channel_id'] = 'DirectMessage'
        elif self.channel_type == 'channel':
            payload['subject'] = "#%s - %s" % (record_name, payload['author_name'])
            payload['android_channel_id'] = 'ChannelMessage'
        else:
            payload['subject'] = "#%s" % (record_name)
        return payload
