# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from collections import Counter

from giga.modules import get_modules, get_resource_path
from giga.tests.common import TransactionCase
from giga.tools.translate import TranslationFileReader


class PotLinter(TransactionCase):
    def test_pot_duplicate_entries(self):
        def format(entry):
            # TranslationFileReader only returns those three types
            if entry['type'] == 'model':
                return ('model', entry['name'], entry['imd_name'])
            elif entry['type'] == 'model_terms':
                return ('model_terms', entry['name'], entry['imd_name'], entry['src'])
            elif entry['type'] == 'code':
                return ('code', entry['src'])

        # retrieve all modules, and their corresponding POT file
        for module in get_modules():
            filename = get_resource_path(module, 'i18n', module + '.pot')
            if not filename:
                continue
            counts = Counter(map(format, TranslationFileReader(filename)))
            duplicates = [key for key, count in counts.items() if count > 1]
            self.assertFalse(duplicates, "Duplicate entries found in %s" % filename)
