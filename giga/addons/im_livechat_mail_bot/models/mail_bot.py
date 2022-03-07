# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, _


class MailBot(models.AbstractModel):
    _inherit = 'mail.bot'

    def _get_answer(self, record, body, values, command):
        gigabot_state = self.env.user.gigabot_state
        if self._is_bot_in_private_channel(record):
            if gigabot_state == "onboarding_attachement" and values.get("attachment_ids"):
                self.env.user.gigabot_failed = False
                self.env.user.gigabot_state = "onboarding_canned"
                return _("That's me! 🎉<br/>Try typing <span class=\"o_gigabot_command\">:</span> to use canned responses.")
            elif gigabot_state == "onboarding_canned" and values.get("canned_response_ids"):
                self.env.user.gigabot_failed = False
                self.env.user.gigabot_state = "idle"
                return _("Good, you can customize canned responses in the live chat application.<br/><br/><b>It's the end of this overview</b>, enjoy discovering Giga!")
            # repeat question if needed
            elif gigabot_state == 'onboarding_canned' and not self._is_help_requested(body):
                self.env.user.gigabot_failed = True
                return _("Not sure what you are doing. Please, type <span class=\"o_gigabot_command\">:</span> and wait for the propositions. Select one of them and press enter.")
        return super(MailBot, self)._get_answer(record, body, values, command)
