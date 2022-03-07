# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import giga

# ----------------------------------------------------------
# Monkey patch release to set the edition as 'enterprise'
# ----------------------------------------------------------
giga.release.version_info = giga.release.version_info[:5] + ('e',)
if '+e' not in giga.release.version:     # not already patched by packaging
    giga.release.version = '{0}+e{1}{2}'.format(*giga.release.version.partition('-'))

giga.service.common.RPC_VERSION_1.update(
    server_version=giga.release.version,
    server_version_info=giga.release.version_info)
