# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

# This assumes an existing but uninitialized database.

from contextlib import contextmanager
import unittest

from giga import api, registry, SUPERUSER_ID
from giga.tests import common
from giga.tests.common import BaseCase

from giga.modules.registry import Registry


@contextmanager
def environment():
    """ Return an environment with a new cursor for the current database; the
        cursor is committed and closed after the context block.
    """
    reg = registry(common.get_db_name())
    with reg.cursor() as cr:
        yield api.Environment(cr, SUPERUSER_ID, {})


MODULE = 'test_uninstall'
MODEL = 'test_uninstall.model'


class TestUninstall(BaseCase):
    """
    Test the install/uninstall of a test module. The module is available in
    `giga.tests` which should be present in the addons-path.
    """

    def test_01_install(self):
        """ Check a few things showing the module is installed. """
        with environment() as env:
            module = env['ir.module.module'].search([('name', '=', MODULE)])
            assert len(module) == 1
            module.button_install()
        Registry.new(common.get_db_name(), update_module=True)

        with environment() as env:
            self.assertIn('test_uninstall.model', env.registry)
            self.assertTrue(env['ir.model.data'].search([('module', '=', MODULE)]))
            self.assertTrue(env['ir.model.fields'].search([('model', '=', MODEL)]))

    def test_02_uninstall(self):
        """ Check a few things showing the module is uninstalled. """
        with environment() as env:
            module = env['ir.module.module'].search([('name', '=', MODULE)])
            assert len(module) == 1
            module.button_uninstall()
        Registry.new(common.get_db_name(), update_module=True)

        with environment() as env:
            self.assertNotIn('test_uninstall.model', env.registry)
            self.assertFalse(env['ir.model.data'].search([('module', '=', MODULE)]))
            self.assertFalse(env['ir.model.fields'].search([('model', '=', MODEL)]))


if __name__ == '__main__':
    unittest.main()
