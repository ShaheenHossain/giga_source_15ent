# -*- coding: utf-8 -*-

from giga import registry, SUPERUSER_ID
from giga.api import Environment
from giga.addons.bus.controllers import main
from giga.fields import Datetime
from giga.http import Controller, request, route


class BusController(main.BusController):

    @route('/longpolling/poll', type="json", auth="public")
    def poll(self, channels, last, options=None):
        if request.env.user.has_group('base.group_user'):
            ip_address = request.httprequest.remote_addr
            users_log = request.env['res.users.log'].search_count([
                ('create_uid', '=', request.env.user.id),
                ('ip', '=', ip_address),
                ('create_date', '>=', Datetime.to_string(Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)))])
            if not users_log:
                with registry(request.env.cr.dbname).cursor() as cr:
                    env = Environment(cr, request.env.user.id, {})
                    env['res.users.log'].create({'ip': ip_address})
        return super(BusController, self).poll(channels, last, options=options)
