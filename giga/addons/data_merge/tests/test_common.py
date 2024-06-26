# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.
import unittest

from giga.tests.common import TransactionCase

class TestCommon(TransactionCase):
    def setUp(self):
        super(TestCommon, self).setUp()

        self.DMModel  = self.env['data_merge.model']
        self.DMRule   = self.env['data_merge.rule']
        self.DMGroup  = self.env['data_merge.group']
        self.DMRecord = self.env['data_merge.record']

        self.DMTestModel = self.env['ir.model'].create({
            'name': 'Test Model',
            'model': 'x_dm_test_model',
            'field_id': [
                (0, 0, {'name': 'x_name', 'ttype': 'char', 'field_description': 'Name'}),
                (0, 0, {'name': 'x_email', 'ttype': 'char', 'field_description': 'Email'}),
            ]
        })

        self.DMTestModelRef = self.env['ir.model'].create({
            'name': 'Test Model Ref',
            'model': 'x_dm_test_model_ref',
            'field_id': [
                (0, 0, {'name': 'x_name', 'ttype': 'char', 'field_description': 'Name'}),
                (0, 0, {'name': 'x_test_id', 'ttype': 'many2one', 'field_description': 'Test Ref', 'relation': 'x_dm_test_model', 'index': True}),
            ]
        })

        self.MyModel = self.DMModel.create({
            'name': 'test of test model',
            'res_model_id': self.DMTestModel.id,
        })
        
    def _create_record(self, model, **kwargs):
        return self.env[model].create(kwargs)

    def _create_rule(self, field_name, mode):
        if mode == 'accent' and not self.registry.has_unaccent:
            raise unittest.SkipTest("Unaccent rules require unaccent to be enabled")
        self.DMRule.create({
            'model_id': self.MyModel.id,
            'field_id': self.env['ir.model.fields']._get('x_dm_test_model', field_name).id,
            'match_mode': mode
        })
