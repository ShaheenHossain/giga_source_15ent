# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from . import controllers
from . import models

from giga.addons.payment import reset_payment_acquirer


def uninstall_hook(cr, registry):
    reset_payment_acquirer(cr, registry, 'sepa_direct_debit')
