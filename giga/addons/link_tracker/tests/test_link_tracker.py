# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga.tests import common
from giga.exceptions import UserError


class TestLinkTracker(common.TransactionCase):
    def test_create(self):
        link_trackers = self.env['link.tracker'].create([
            {
                'url': 'gigasource.de',
                'title': 'Giga',
            }, {
                'url': 'example.com',
                'title': 'Giga',
            }, {
                'url': 'http://test.example.com',
                'title': 'Giga',
            },
        ])

        self.assertEqual(
            link_trackers.mapped('url'),
            ['http://gigasource.de', 'http://example.com', 'http://test.example.com'],
        )

        self.assertEqual(len(set(link_trackers.mapped('code'))), 3)

    def test_search_or_create(self):
        link_tracker_1 = self.env['link.tracker'].create({
            'url': 'https://gigasource.de',
            'title': 'Giga',
        })

        link_tracker_2 = self.env['link.tracker'].search_or_create({
            'url': 'https://gigasource.de',
            'title': 'Giga',
        })

        self.assertEqual(link_tracker_1, link_tracker_2)

        link_tracker_3 = self.env['link.tracker'].search_or_create({
            'url': 'https://giga.be',
            'title': 'Giga',
        })

        self.assertNotEqual(link_tracker_1, link_tracker_3)

    def test_constraint(self):
        campaign_id = self.env['utm.campaign'].search([], limit=1)

        self.env['link.tracker'].create({
            'url': 'https://gigasource.de',
            'title': 'Giga',
        })

        link_1 = self.env['link.tracker'].create({
            'url': '2nd url',
            'title': 'Giga',
            'campaign_id': campaign_id.id,
        })

        with self.assertRaises(UserError):
            self.env['link.tracker'].create({
                'url': 'https://gigasource.de',
                'title': 'Giga',
            })

        with self.assertRaises(UserError):
            self.env['link.tracker'].create({
                'url': '2nd url',
                'title': 'Giga',
                'campaign_id': campaign_id.id,
            })

        link_2 = self.env['link.tracker'].create({
                'url': '2nd url',
                'title': 'Giga',
                'campaign_id': campaign_id.id,
                'medium_id': self.env['utm.medium'].search([], limit=1).id
            })

        # test in batch
        with self.assertRaises(UserError):
            # both link trackers on which we write will have the same values
            (link_1 | link_2).write({'campaign_id': False, 'medium_id': False})

        with self.assertRaises(UserError):
            (link_1 | link_2).write({'medium_id': False})
