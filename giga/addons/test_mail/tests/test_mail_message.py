# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import base64
from unittest.mock import patch

from giga.addons.mail.tests.common import mail_new_test_user
from giga.addons.test_mail.tests.common import TestMailCommon
from giga.addons.test_mail.models.test_mail_models import MailTestSimple
from giga.exceptions import AccessError
from giga.tools import mute_logger, formataddr
from giga.tests import tagged


class TestMessageValues(TestMailCommon):

    @classmethod
    def setUpClass(cls):
        super(TestMessageValues, cls).setUpClass()

        cls._init_mail_gateway()
        cls.alias_record = cls.env['mail.test.container'].with_context(cls._test_context).create({
            'name': 'Pigs',
            'alias_name': 'pigs',
            'alias_contact': 'followers',
        })
        cls.Message = cls.env['mail.message'].with_user(cls.user_employee)

    @mute_logger('giga.models.unlink')
    def test_mail_message_format(self):
        record1 = self.env['mail.test.simple'].create({'name': 'Test1'})
        message = self.env['mail.message'].create([{
            'model': 'mail.test.simple',
            'res_id': record1.id,
        }])
        res = message.message_format()
        self.assertEqual(res[0].get('record_name'), 'Test1')

        record1.write({"name": "Test2"})
        res = message.message_format()
        self.assertEqual(res[0].get('record_name'), 'Test2')

    @mute_logger('giga.models.unlink')
    def test_mail_message_format_access(self):
        """
        User that doesn't have access to a record should still be able to fetch
        the record_name inside message_format.
        """
        company_2 = self.env['res.company'].create({'name': 'Second Test Company'})
        record1 = self.env['mail.test.multi.company'].create({
            'name': 'Test1',
            'company_id': company_2.id,
        })
        message = record1.message_post(body='', partner_ids=[self.user_employee.partner_id.id])
        # We need to flush and invalidate the ORM cache since the record_name
        # is already cached from the creation. Otherwise it will leak inside
        # message_format.
        message.flush()
        message.invalidate_cache()
        res = message.with_user(self.user_employee).message_format()
        self.assertEqual(res[0].get('record_name'), 'Test1')

    @mute_logger('giga.models.unlink')
    def test_mail_message_values_no_document_values(self):
        msg = self.Message.create({
            'reply_to': 'test.reply@example.com',
            'email_from': 'test.from@example.com',
        })
        self.assertIn('-private', msg.message_id.split('@')[0], 'mail_message: message_id for a void message should be a "private" one')
        self.assertEqual(msg.reply_to, 'test.reply@example.com')
        self.assertEqual(msg.email_from, 'test.from@example.com')

    @mute_logger('giga.models.unlink')
    def test_mail_message_values_no_document(self):
        msg = self.Message.create({})
        self.assertIn('-private', msg.message_id.split('@')[0], 'mail_message: message_id for a void message should be a "private" one')
        reply_to_name = self.env.user.company_id.name
        reply_to_email = '%s@%s' % (self.alias_catchall, self.alias_domain)
        self.assertEqual(msg.reply_to, formataddr((reply_to_name, reply_to_email)))
        self.assertEqual(msg.email_from, formataddr((self.user_employee.name, self.user_employee.email)))

        # no alias domain -> author
        self.env['ir.config_parameter'].search([('key', '=', 'mail.catchall.domain')]).unlink()

        msg = self.Message.create({})
        self.assertIn('-private', msg.message_id.split('@')[0], 'mail_message: message_id for a void message should be a "private" one')
        self.assertEqual(msg.reply_to, formataddr((self.user_employee.name, self.user_employee.email)))
        self.assertEqual(msg.email_from, formataddr((self.user_employee.name, self.user_employee.email)))

        # no alias catchall, no alias -> author
        self.env['ir.config_parameter'].set_param('mail.catchall.domain', self.alias_domain)
        self.env['ir.config_parameter'].search([('key', '=', 'mail.catchall.alias')]).unlink()

        msg = self.Message.create({})
        self.assertIn('-private', msg.message_id.split('@')[0], 'mail_message: message_id for a void message should be a "private" one')
        self.assertEqual(msg.reply_to, formataddr((self.user_employee.name, self.user_employee.email)))
        self.assertEqual(msg.email_from, formataddr((self.user_employee.name, self.user_employee.email)))

    @mute_logger('giga.models.unlink')
    def test_mail_message_values_document_alias(self):
        msg = self.Message.create({
            'model': 'mail.test.container',
            'res_id': self.alias_record.id
        })
        self.assertIn('-openerp-%d-mail.test' % self.alias_record.id, msg.message_id.split('@')[0])
        reply_to_name = '%s %s' % (self.env.user.company_id.name, self.alias_record.name)
        reply_to_email = '%s@%s' % (self.alias_record.alias_name, self.alias_domain)
        self.assertEqual(msg.reply_to, formataddr((reply_to_name, reply_to_email)))
        self.assertEqual(msg.email_from, formataddr((self.user_employee.name, self.user_employee.email)))

        # no alias domain -> author
        self.env['ir.config_parameter'].search([('key', '=', 'mail.catchall.domain')]).unlink()

        msg = self.Message.create({
            'model': 'mail.test.container',
            'res_id': self.alias_record.id
        })
        self.assertIn('-openerp-%d-mail.test' % self.alias_record.id, msg.message_id.split('@')[0])
        self.assertEqual(msg.reply_to, formataddr((self.user_employee.name, self.user_employee.email)))
        self.assertEqual(msg.email_from, formataddr((self.user_employee.name, self.user_employee.email)))

        # no catchall -> don't care, alias
        self.env['ir.config_parameter'].set_param('mail.catchall.domain', self.alias_domain)
        self.env['ir.config_parameter'].search([('key', '=', 'mail.catchall.alias')]).unlink()

        msg = self.Message.create({
            'model': 'mail.test.container',
            'res_id': self.alias_record.id
        })
        self.assertIn('-openerp-%d-mail.test' % self.alias_record.id, msg.message_id.split('@')[0])
        reply_to_name = '%s %s' % (self.env.company.name, self.alias_record.name)
        reply_to_email = '%s@%s' % (self.alias_record.alias_name, self.alias_domain)
        self.assertEqual(msg.reply_to, formataddr((reply_to_name, reply_to_email)))
        self.assertEqual(msg.email_from, formataddr((self.user_employee.name, self.user_employee.email)))

    @mute_logger('giga.models.unlink')
    def test_mail_message_values_document_no_alias(self):
        test_record = self.env['mail.test.simple'].create({'name': 'Test', 'email_from': 'ignasse@example.com'})

        msg = self.Message.create({
            'model': 'mail.test.simple',
            'res_id': test_record.id
        })
        self.assertIn('-openerp-%d-mail.test.simple' % test_record.id, msg.message_id.split('@')[0])
        reply_to_name = '%s %s' % (self.env.user.company_id.name, test_record.name)
        reply_to_email = '%s@%s' % (self.alias_catchall, self.alias_domain)
        self.assertEqual(msg.reply_to, formataddr((reply_to_name, reply_to_email)))
        self.assertEqual(msg.email_from, formataddr((self.user_employee.name, self.user_employee.email)))

    @mute_logger('giga.models.unlink')
    def test_mail_message_values_document_manual_alias(self):
        test_record = self.env['mail.test.simple'].create({'name': 'Test', 'email_from': 'ignasse@example.com'})
        alias = self.env['mail.alias'].create({
            'alias_name': 'MegaLias',
            'alias_user_id': False,
            'alias_model_id': self.env['ir.model']._get('mail.test.simple').id,
            'alias_parent_model_id': self.env['ir.model']._get('mail.test.simple').id,
            'alias_parent_thread_id': test_record.id,
        })

        msg = self.Message.create({
            'model': 'mail.test.simple',
            'res_id': test_record.id
        })

        self.assertIn('-openerp-%d-mail.test.simple' % test_record.id, msg.message_id.split('@')[0])
        reply_to_name = '%s %s' % (self.env.user.company_id.name, test_record.name)
        reply_to_email = '%s@%s' % (alias.alias_name, self.alias_domain)
        self.assertEqual(msg.reply_to, formataddr((reply_to_name, reply_to_email)))
        self.assertEqual(msg.email_from, formataddr((self.user_employee.name, self.user_employee.email)))

    def test_mail_message_values_reply_to_force_new(self):
        msg = self.Message.create({
            'model': 'mail.test.container',
            'res_id': self.alias_record.id,
            'reply_to_force_new': True,
        })
        self.assertIn('reply_to', msg.message_id.split('@')[0])
        self.assertNotIn('mail.test.container', msg.message_id.split('@')[0])
        self.assertNotIn('-%d-' % self.alias_record.id, msg.message_id.split('@')[0])

    def test_mail_message_base64_image(self):
        msg = self.env['mail.message'].with_user(self.user_employee).create({
            'body': 'taratata <img src="data:image/png;base64,iV/+OkI=" width="2"> <img src="data:image/png;base64,iV/+OkI=" width="2">',
        })
        self.assertEqual(len(msg.attachment_ids), 1)
        body = '<p>taratata <img src="/web/image/%s?access_token=%s" alt="image0" width="2"> <img src="/web/image/%s?access_token=%s" alt="image0" width="2"></p>'
        body = body % (msg.attachment_ids[0].id, msg.attachment_ids[0].access_token, msg.attachment_ids[0].id, msg.attachment_ids[0].access_token)
        self.assertEqual(msg.body, body)


class TestMessageAccess(TestMailCommon):

    @classmethod
    def setUpClass(cls):
        super(TestMessageAccess, cls).setUpClass()

        cls.user_public = mail_new_test_user(cls.env, login='bert', groups='base.group_public', name='Bert Tartignole')
        cls.user_portal = mail_new_test_user(cls.env, login='chell', groups='base.group_portal', name='Chell Gladys')

        Channel = cls.env['mail.channel'].with_context(cls._test_context)
        # Pigs: base group for tests
        cls.group_pigs = Channel.create({
            'name': 'Pigs',
            'public': 'groups',
            'group_public_id': cls.env.ref('base.group_user').id})
        # Jobs: public group
        cls.group_public = Channel.create({
            'name': 'Jobs',
            'description': 'NotFalse',
            'public': 'public'})
        # Private: private gtroup
        cls.group_private = Channel.create({
            'name': 'Private',
            'public': 'private'})
        cls.message = cls.env['mail.message'].create({
            'body': 'My Body',
            'model': 'mail.channel',
            'res_id': cls.group_private.id,
        })

    @mute_logger('giga.addons.mail.models.mail_mail')
    def test_mail_message_access_search(self):
        # Data: various author_ids, partner_ids, documents
        msg1 = self.env['mail.message'].create({
            'subject': '_ZTest', 'body': 'A', 'subtype_id': self.ref('mail.mt_comment')})
        msg2 = self.env['mail.message'].create({
            'subject': '_ZTest', 'body': 'A+B', 'subtype_id': self.ref('mail.mt_comment'),
            'partner_ids': [(6, 0, [self.user_public.partner_id.id])]})
        msg3 = self.env['mail.message'].create({
            'subject': '_ZTest', 'body': 'A Pigs', 'subtype_id': False,
            'model': 'mail.channel', 'res_id': self.group_pigs.id})
        msg4 = self.env['mail.message'].create({
            'subject': '_ZTest', 'body': 'A+P Pigs', 'subtype_id': self.ref('mail.mt_comment'),
            'model': 'mail.channel', 'res_id': self.group_pigs.id,
            'partner_ids': [(6, 0, [self.user_public.partner_id.id])]})
        msg5 = self.env['mail.message'].create({
            'subject': '_ZTest', 'body': 'A+E Pigs', 'subtype_id': self.ref('mail.mt_comment'),
            'model': 'mail.channel', 'res_id': self.group_pigs.id,
            'partner_ids': [(6, 0, [self.user_employee.partner_id.id])]})
        msg6 = self.env['mail.message'].create({
            'subject': '_ZTest', 'body': 'A Birds', 'subtype_id': self.ref('mail.mt_comment'),
            'model': 'mail.channel', 'res_id': self.group_private.id})
        msg7 = self.env['mail.message'].with_user(self.user_employee).create({
            'subject': '_ZTest', 'body': 'B', 'subtype_id': self.ref('mail.mt_comment')})
        msg8 = self.env['mail.message'].with_user(self.user_employee).create({
            'subject': '_ZTest', 'body': 'B+E', 'subtype_id': self.ref('mail.mt_comment'),
            'partner_ids': [(6, 0, [self.user_employee.partner_id.id])]})

        # Test: Public: 2 messages (recipient)
        messages = self.env['mail.message'].with_user(self.user_public).search([('subject', 'like', '_ZTest')])
        self.assertEqual(messages, msg2 | msg4)

        # Test: Employee: 3 messages on Pigs Raoul can read (employee can read group with default values)
        messages = self.env['mail.message'].with_user(self.user_employee).search([('subject', 'like', '_ZTest'), ('body', 'ilike', 'A')])
        self.assertEqual(messages, msg3 | msg4 | msg5)

        # Test: Raoul: 3 messages on Pigs Raoul can read (employee can read group with default values), 0 on Birds (private group) + 2 messages as author
        messages = self.env['mail.message'].with_user(self.user_employee).search([('subject', 'like', '_ZTest')])
        self.assertEqual(messages, msg3 | msg4 | msg5 | msg7 | msg8)

        # Test: Admin: all messages
        messages = self.env['mail.message'].search([('subject', 'like', '_ZTest')])
        self.assertEqual(messages, msg1 | msg2 | msg3 | msg4 | msg5 | msg6 | msg7 | msg8)

        # Test: Portal: 0 (no access to groups, not recipient)
        messages = self.env['mail.message'].with_user(self.user_portal).search([('subject', 'like', '_ZTest')])
        self.assertFalse(messages)

        # Test: Portal: 2 messages (public group with a subtype)
        self.group_pigs.write({'public': 'public'})
        messages = self.env['mail.message'].with_user(self.user_portal).search([('subject', 'like', '_ZTest')])
        self.assertEqual(messages, msg4 | msg5)

    # --------------------------------------------------
    # READ
    # --------------------------------------------------

    @mute_logger('giga.addons.base.models.ir_model', 'giga.models')
    def test_mail_message_access_read_crash(self):
        with self.assertRaises(AccessError):
            self.message.with_user(self.user_employee).read()

    @mute_logger('giga.models')
    def test_mail_message_access_read_crash_portal(self):
        with self.assertRaises(AccessError):
            self.message.with_user(self.user_portal).read(['body', 'message_type', 'subtype_id'])

    def test_mail_message_access_read_ok_portal(self):
        self.message.write({'subtype_id': self.ref('mail.mt_comment'), 'res_id': self.group_public.id})
        self.message.with_user(self.user_portal).read(['body', 'message_type', 'subtype_id'])

    def test_mail_message_access_read_notification(self):
        attachment = self.env['ir.attachment'].create({
            'datas': base64.b64encode(b'My attachment'),
            'name': 'doc.txt'})
        # attach the attachment to the message
        self.message.write({'attachment_ids': [(4, attachment.id)]})
        self.message.write({'partner_ids': [(4, self.user_employee.partner_id.id)]})
        self.message.with_user(self.user_employee).read()
        # Test: Bert has access to attachment, ok because he can read message
        attachment.with_user(self.user_employee).read(['name', 'datas'])

    def test_mail_message_access_read_author(self):
        self.message.write({'author_id': self.user_employee.partner_id.id})
        self.message.with_user(self.user_employee).read()

    def test_mail_message_access_read_doc(self):
        self.message.write({'model': 'mail.channel', 'res_id': self.group_public.id})
        # Test: Bert reads the message, ok because linked to a doc he is allowed to read
        self.message.with_user(self.user_employee).read()

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------

    @mute_logger('giga.addons.base.models.ir_model')
    def test_mail_message_access_create_crash_public(self):
        # Do: Bert creates a message on Pigs -> ko, no creation rights
        with self.assertRaises(AccessError):
            self.env['mail.message'].with_user(self.user_public).create({'model': 'mail.channel', 'res_id': self.group_pigs.id, 'body': 'Test'})

        # Do: Bert create a message on Jobs -> ko, no creation rights
        with self.assertRaises(AccessError):
            self.env['mail.message'].with_user(self.user_public).create({'model': 'mail.channel', 'res_id': self.group_public.id, 'body': 'Test'})

    @mute_logger('giga.models')
    def test_mail_message_access_create_crash(self):
        # Do: Bert create a private message -> ko, no creation rights
        with self.assertRaises(AccessError):
            self.env['mail.message'].with_user(self.user_employee).create({'model': 'mail.channel', 'res_id': self.group_private.id, 'body': 'Test'})

    @mute_logger('giga.models')
    def test_mail_message_access_create_doc(self):
        Message = self.env['mail.message'].with_user(self.user_employee)
        # Do: Raoul creates a message on Jobs -> ok, write access to the related document
        Message.create({'model': 'mail.channel', 'res_id': self.group_public.id, 'body': 'Test'})
        # Do: Raoul creates a message on Priv -> ko, no write access to the related document
        with self.assertRaises(AccessError):
            Message.create({'model': 'mail.channel', 'res_id': self.group_private.id, 'body': 'Test'})

    def test_mail_message_access_create_private(self):
        self.env['mail.message'].with_user(self.user_employee).create({'body': 'Test'})

    def test_mail_message_access_create_reply(self):
        # TDE FIXME: should it really work ? not sure - catchall makes crash (aka, post will crash also)
        self.env['ir.config_parameter'].set_param('mail.catchall.domain', False)
        self.message.write({'partner_ids': [(4, self.user_employee.partner_id.id)]})
        self.env['mail.message'].with_user(self.user_employee).create({'model': 'mail.channel', 'res_id': self.group_private.id, 'body': 'Test', 'parent_id': self.message.id})

    def test_mail_message_access_create_wo_parent_access(self):
        """ Purpose is to test posting a message on a record whose first message / parent
        is not accessible by current user. """
        test_record = self.env['mail.test.simple'].with_context(self._test_context).create({'name': 'Test', 'email_from': 'ignasse@example.com'})
        partner_1 = self.env['res.partner'].create({
            'name': 'Jitendra Prajapati (jpr-giga)',
            'email': 'jpr@gigasource.de',
        })
        test_record.message_subscribe((partner_1 | self.user_admin.partner_id).ids)

        message = test_record.message_post(
            body='<p>This is First Message</p>', subject='Subject',
            message_type='comment', subtype_xmlid='mail.mt_note')
        # portal user have no rights to read the message
        with self.assertRaises(AccessError):
            message.with_user(self.user_portal).read(['subject, body'])

        with patch.object(MailTestSimple, 'check_access_rights', return_value=True):
            with self.assertRaises(AccessError):
                message.with_user(self.user_portal).read(['subject, body'])

            # parent message is accessible to references notification mail values
            # for _notify method and portal user have no rights to send the message for this model
            new_msg = test_record.with_user(self.user_portal).message_post(
                body='<p>This is Second Message</p>',
                subject='Subject',
                parent_id=message.id,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                mail_auto_delete=False)

        new_mail = self.env['mail.mail'].sudo().search([
            ('mail_message_id', '=', new_msg.id),
            ('references', '=', message.message_id),
        ])

        self.assertTrue(new_mail)
        self.assertEqual(new_msg.parent_id, message)
