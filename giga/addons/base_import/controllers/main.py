# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import json

from giga import http
from giga.http import request
from giga.tools import misc


class ImportController(http.Controller):

    @http.route('/base_import/set_file', methods=['POST'])
    def set_file(self, file, import_id, jsonp='callback'):
        import_id = int(import_id)

        written = request.env['base_import.import'].browse(import_id).write({
            'file': file.read(),
            'file_name': file.filename,
            'file_type': file.content_type,
        })

        return 'window.top.%s(%s)' % (misc.html_escape(jsonp), json.dumps({'result': written}))
