# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga.addons.social.tests import common
from giga.exceptions import AccessError
from giga.tests import tagged
from giga.tests.common import users
from giga.tools import mute_logger


@tagged('security')
class TestAccess(common.SocialCase):
    @classmethod
    def setUpClass(cls):
        """ Create some more dummy data for security tests. """
        super(TestAccess, cls).setUpClass()

        cls.social_live_post = cls.env['social.live.post'].create({
            'post_id': cls.social_post.id,
            'account_id': cls.social_account.id
        })

        cls.social_stream_type = cls.env['social.stream.type'].create({
            'name': 'My Stream Type',
            'stream_type': 'my_stream_type',
            'media_id': cls.social_media.id
        })

        cls.social_stream = cls.env['social.stream'].create({
            'account_id': cls.social_account.id,
            'stream_type_id': cls.social_stream_type.id,
            'media_id': cls.social_media.id
        })

        cls.social_stream_post = cls.env['social.stream.post'].create({
            'message': 'A stream post',
            'stream_id': cls.social_stream.id,
        })

        cls.social_stream_post_image = cls.env['social.stream.post.image'].create({
            'stream_post_id': cls.social_stream_post.id,
            'image_url': 'dummy.png'
        })

    @mute_logger('giga.addons.base.models.ir_model')
    @users('user_emp')
    def test_access_social_employee(self):
        # Create: not allowed
        with self.assertRaises(AccessError):
            self.env['social.post'].create({'message': 'A Post'})
        with self.assertRaises(AccessError):
            self.env['social.live.post'].create({'post_id': self.social_post.id, 'account_id': self.social_account.id})
        with self.assertRaises(AccessError):
            self.env['social.account'].create({'name': 'An account'})
        with self.assertRaises(AccessError):
            self.env['social.media'].create({'name': 'A media'})
        with self.assertRaises(AccessError):
            self.env['social.stream'].create({'name': 'A stream', 'account_id': self.social_account.id})
        with self.assertRaises(AccessError):
            self.env['social.stream.type'].create({'name': 'A stream type'})
        with self.assertRaises(AccessError):
            self.env['social.stream.post'].create({'message': 'A stream post'})
        with self.assertRaises(AccessError):
            self.env['social.stream.post.image'].create({'image_url': 'dummy.png'})

        # Read: not allowed
        with self.assertRaises(AccessError):
            self.social_post.with_user(self.env.user).read(['message'])
        with self.assertRaises(AccessError):
            self.social_live_post.with_user(self.env.user).read(['post_id'])
        with self.assertRaises(AccessError):
            self.social_account.with_user(self.env.user).read(['name'])
        with self.assertRaises(AccessError):
            self.social_media.with_user(self.env.user).read(['name'])
        with self.assertRaises(AccessError):
            self.social_stream.with_user(self.env.user).read(['media_id'])
        with self.assertRaises(AccessError):
            self.social_stream_type.with_user(self.env.user).read(['media_id'])
        with self.assertRaises(AccessError):
            self.social_stream_post.with_user(self.env.user).read(['message'])
        with self.assertRaises(AccessError):
            self.social_stream_post_image.with_user(self.env.user).read(['stream_post_id'])

        # Write: not allowed
        with self.assertRaises(AccessError):
            self.social_post.with_user(self.env.user).write({'message': 'New Message'})
        with self.assertRaises(AccessError):
            self.social_live_post.with_user(self.env.user).write({'post_id': self.social_post.id})
        with self.assertRaises(AccessError):
            self.social_account.with_user(self.env.user).write({'name': 'New Name'})
        with self.assertRaises(AccessError):
            self.social_media.with_user(self.env.user).write({'name': 'New Name'})
        with self.assertRaises(AccessError):
            self.social_stream.with_user(self.env.user).write({'media_id': self.social_media.id})
        with self.assertRaises(AccessError):
            self.social_stream_type.with_user(self.env.user).write({'media_id': self.social_media.id})
        with self.assertRaises(AccessError):
            self.social_stream_post.with_user(self.env.user).write({'message': 'New Message'})
        with self.assertRaises(AccessError):
            self.social_stream_post_image.with_user(self.env.user).write({'stream_post_id': self.social_stream_post.id})

        # Unlink: not allowed
        with self.assertRaises(AccessError):
            self.social_post.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_live_post.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_account.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_media.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_stream.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_stream_type.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_stream_post.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_stream_post_image.with_user(self.env.user).unlink()

    @mute_logger('giga.addons.base.models.ir_model')
    @users('social_user')
    def test_access_social_social_user(self):
        # Create: not allowed except for posts and streams
        new_post = self.env['social.post'].create({'message': 'A Post'})
        new_stream = self.env['social.stream'].create({
            'media_id': self.social_media.id,
            'stream_type_id': self.social_stream_type.id,
            'account_id': self.social_account.id
        })
        with self.assertRaises(AccessError):
            self.env['social.live.post'].create({'post_id': self.social_post.id, 'account_id': self.social_account.id})
        with self.assertRaises(AccessError):
            self.env['social.account'].create({'name': 'An account'})
        with self.assertRaises(AccessError):
            self.env['social.media'].create({'name': 'A media'})
        with self.assertRaises(AccessError):
            self.env['social.stream.type'].create({'name': 'A stream type'})
        with self.assertRaises(AccessError):
            self.env['social.stream.post'].create({'message': 'A stream post'})
        with self.assertRaises(AccessError):
            self.env['social.stream.post.image'].create({'image_url': 'dummy.png'})

        # Can't post
        with self.assertRaises(AccessError):
            new_post.action_post()

        # Read: allowed (except for posts, he can only read his own)
        new_post.with_user(self.env.user).read(['message'])
        with self.assertRaises(AccessError):
            self.social_post.with_user(self.env.user).read(['message'])
        self.social_live_post.with_user(self.env.user).read(['post_id'])
        self.social_account.with_user(self.env.user).read(['name'])
        self.social_media.with_user(self.env.user).read(['name'])
        self.social_stream.with_user(self.env.user).read(['media_id'])
        self.social_stream_type.with_user(self.env.user).read(['media_id'])
        self.social_stream_post.with_user(self.env.user).read(['message'])
        self.social_stream_post_image.with_user(self.env.user).read(['stream_post_id'])

        # Write: not allowed except for his own posts/streams (and never on the state field)
        new_post.with_user(self.env.user).write({'message': 'New Message'})
        new_stream.with_user(self.env.user).write({'name': 'New Name'})
        with self.assertRaises(AccessError):
            self.social_post.with_user(self.env.user).write({'message': 'New Message'})
        # can't write on the 'state' field
        with self.assertRaises(AccessError):
            new_post.with_user(self.env.user).write({'state': 'scheduled'})
        with self.assertRaises(AccessError):
            self.social_live_post.with_user(self.env.user).write({'post_id': self.social_post.id})
        with self.assertRaises(AccessError):
            self.social_account.with_user(self.env.user).write({'name': 'New Name'})
        with self.assertRaises(AccessError):
            self.social_media.with_user(self.env.user).write({'name': 'New Name'})
        with self.assertRaises(AccessError):
            self.social_stream.with_user(self.env.user).write({'media_id': self.social_media.id})
        with self.assertRaises(AccessError):
            self.social_stream_type.with_user(self.env.user).write({'media_id': self.social_media.id})
        with self.assertRaises(AccessError):
            self.social_stream_post.with_user(self.env.user).write({'message': 'New Message'})
        with self.assertRaises(AccessError):
            self.social_stream_post_image.with_user(self.env.user).write({'stream_post_id': self.social_stream_post.id})

        # Unlink: not allowed except for his own posts/streams
        new_post.with_user(self.env.user).unlink()
        new_stream.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_post.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_live_post.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_account.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_media.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_stream.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_stream_type.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_stream_post.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_stream_post_image.with_user(self.env.user).unlink()

    @mute_logger('giga.addons.base.models.ir_model')
    @users('social_manager')
    def test_access_social_social_manager(self):
        # Create: allowed except for media and stream types
        new_post = self.env['social.post'].create({'message': 'A Post', 'account_ids': [(4, self.social_account.id)]})
        self.env['social.live.post'].create({'post_id': self.social_post.id, 'account_id': self.social_account.id})
        self.env['social.account'].create({'name': 'An account', 'media_id': self.social_media.id})
        self.env['social.stream'].create({
            'media_id': self.social_media.id,
            'stream_type_id': self.social_stream_type.id,
            'account_id': self.social_account.id
        })
        self.env['social.stream.post'].create({'message': 'A stream post', 'stream_id': self.social_stream.id})
        self.env['social.stream.post.image'].create({'image_url': 'dummy.png'})

        with self.assertRaises(AccessError):
            self.env['social.media'].create({'name': 'A media'})
        with self.assertRaises(AccessError):
            self.env['social.stream.type'].create({'name': 'A stream type'})

        # Can post
        new_post.action_post()

        # Read: allowed
        self.social_post.with_user(self.env.user).read(['message'])
        self.social_live_post.with_user(self.env.user).read(['post_id'])
        self.social_account.with_user(self.env.user).read(['name'])
        self.social_media.with_user(self.env.user).read(['name'])
        self.social_stream.with_user(self.env.user).read(['media_id'])
        self.social_stream_type.with_user(self.env.user).read(['media_id'])
        self.social_stream_post.with_user(self.env.user).read(['message'])
        self.social_stream_post_image.with_user(self.env.user).read(['stream_post_id'])

        # Write: allowed except for stream types
        self.social_media.with_user(self.env.user).write({'name': 'New Name'})
        self.social_post.with_user(self.env.user).write({'message': 'New Message', 'state': 'scheduled'})
        self.social_live_post.with_user(self.env.user).write({'post_id': self.social_post.id})
        self.social_account.with_user(self.env.user).write({'name': 'New Name'})
        self.social_stream.with_user(self.env.user).write({'media_id': self.social_media.id})
        self.social_stream_post.with_user(self.env.user).write({'message': 'New Message'})
        self.social_stream_post_image.with_user(self.env.user).write({'stream_post_id': self.social_stream_post.id})

        with self.assertRaises(AccessError):
            self.social_stream_type.with_user(self.env.user).write({'media_id': self.social_media.id})

        # Unlink: allowed except for media and stream types
        self.social_live_post.with_user(self.env.user).unlink()
        self.social_post.with_user(self.env.user).unlink()
        self.social_stream_post_image.with_user(self.env.user).unlink()
        self.social_stream_post.with_user(self.env.user).unlink()
        self.social_stream.with_user(self.env.user).unlink()
        self.social_account.with_user(self.env.user).unlink()

        with self.assertRaises(AccessError):
            self.social_media.with_user(self.env.user).unlink()
        with self.assertRaises(AccessError):
            self.social_stream_type.with_user(self.env.user).unlink()

    @classmethod
    def _get_social_media(cls):
        return cls.env['social.media'].create({
            'name': 'Social Media',
        })
