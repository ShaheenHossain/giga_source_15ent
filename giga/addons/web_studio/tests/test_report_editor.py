from giga.addons.web_studio.controllers.main import WebStudioController
from giga.http import _request_stack
from giga.tests.common import TransactionCase
from giga.tools import DotDict


class TestReportEditor(TransactionCase):

    def setUp(self):
        super(TestReportEditor, self).setUp()
        self.session = DotDict({'debug': False})
        _request_stack.push(self)
        self.WebStudioController = WebStudioController()

    def test_copy_inherit_report(self):
        report = self.env['ir.actions.report'].create({
            'name': 'test inherit report user',
            'report_name': 'web_studio.test_inherit_report_user',
            'model': 'res.users',
        })
        self.env['ir.ui.view'].create({
            'type': 'qweb',
            'name': 'web_studio.test_inherit_report_hi',
            'key': 'web_studio.test_inherit_report_hi',
            'arch': '''
                <t t-name="web_studio.test_inherit_report_hi">
                    hi
                </t>
            ''',
        })
        parent_view = self.env['ir.ui.view'].create({
            'type': 'qweb',
            'name': 'web_studio.test_inherit_report_user_parent',
            'key': 'web_studio.test_inherit_report_user_parent',
            'arch': '''
                <t t-name="web_studio.test_inherit_report_user_parent_view_parent">
                    <t t-call="web_studio.test_inherit_report_hi"/>!
                </t>
            ''',
        })
        self.env['ir.ui.view'].create({
            'type': 'qweb',
            'name': 'web_studio.test_inherit_report_user',
            'key': 'web_studio.test_inherit_report_user',
            'arch': '''
                <xpath expr="." position="inside">
                    <t t-call="web_studio.test_inherit_report_hi"/>!!
                </xpath>
            ''',
            'inherit_id': parent_view.id,

        })

        # check original report render to expected output
        report_html = report._render_template(report.report_name).decode()
        self.assertEqual(''.join(report_html.split()), 'hi!hi!!')

        # duplicate original report
        report.copy_report_and_template()
        copy_report = self.env['ir.actions.report'].search([
            ('report_name', '=', 'web_studio.test_inherit_report_user_copy_1'),
        ])

        # check duplicated report render to expected output
        copy_report_html = copy_report._render_template(copy_report.report_name).decode()
        self.assertEqual(''.join(copy_report_html.split()), 'hi!hi!!')

        # check that duplicated view is inheritance combination of original view
        copy_view = self.env['ir.ui.view'].search([
            ('key', '=', copy_report.report_name),
        ])
        self.assertFalse(copy_view.inherit_id, 'copied view does not inherit another one')
        found = len(copy_view.arch_db.split('test_inherit_report_hi_copy_1')) - 1
        self.assertEqual(found, 2, 't-call is duplicated one time and used 2 times')


    def test_duplicate(self):
        # Inheritance during an upgrade work only with loaded views
        # The following force the inheritance to work for all views
        # so the created view is correctly inherited
        self.env = self.env(context={'load_all_views': True})


        # Create a report/view containing "foo"
        report = self.env['ir.actions.report'].create({
            'name': 'test duplicate',
            'report_name': 'web_studio.test_duplicate_foo',
            'model': 'res.users',})

        self.env['ir.ui.view'].create({
            'type': 'qweb',
            'name': 'test_duplicate_foo',
            'key': 'web_studio.test_duplicate_foo',
            'arch': "<t t-name='web_studio.test_duplicate_foo'>foo</t>",})

        duplicate_domain = [('report_name', '=like', 'web_studio.test_duplicate_foo_copy_%')]

        # Duplicate the report and retrieve the duplicated view
        report.copy_report_and_template()
        copy1 = self.env['ir.actions.report'].search(duplicate_domain)
        copy1.ensure_one()  # watchdog
        copy1_view = self.env['ir.ui.view'].search([
            ('key', '=', copy1.report_name)])
        copy1_view.ensure_one()  # watchdog

        # Inherit the view to replace "foo" by "bar"
        self.env['ir.ui.view'].create({
            'inherit_id': copy1_view.id,
            'key': copy1.report_name,
            'arch': '''
                <xpath expr="." position="replace">
                    <t t-name='%s'>bar</t>
                </xpath>
            ''' % copy1.report_name,})

        # Assert the duplicated view renders "bar" then unlink the report
        copy1_html = copy1._render_template(copy1.report_name).decode()
        self.assertEqual(''.join(copy1_html.split()), 'bar')
        copy1.unlink()

        # Re-duplicate the original report, it must renders "foo"
        report.copy_report_and_template()
        copy2 = self.env['ir.actions.report'].search(duplicate_domain)
        copy2.ensure_one()
        copy2_html = copy2._render_template(copy2.report_name).decode()
        self.assertEqual(''.join(copy2_html.split()), 'foo')

    def test_copy_custom_model_rendering(self):
        report = self.env['ir.actions.report'].search([('report_name', '=', 'base.report_irmodulereference')])
        report.copy_report_and_template()
        copy = self.env['ir.actions.report'].search([('report_name', '=', 'base.report_irmodulereference_copy_1')])
        report_model = copy._get_rendering_context_model()
        self.assertIsNotNone(report_model)

    def test_duplicate_keep_translations(self):
        def create_view(name, **kwargs):
            arch = '<div>{}</div>'.format(name)
            if kwargs.get('inherit_id'):
                arch = '<xpath expr="." path="inside">{}</xpath>'.format(arch)
            name = 'web_studio.test_keep_translations_{}'.format(name)
            return self.env['ir.ui.view'].create(dict({
                'type': 'qweb',
                'name': name,
                'key': name,
                'arch': arch,
            }, **kwargs))

        report = self.env['ir.actions.report'].create({
            'name': 'test inherit report user',
            'report_name': 'web_studio.test_keep_translations_ab',
            'model': 'res.users',
        }).with_context(load_all_views=True)

        self.env.ref('base.lang_fr').active = True
        views = report.env['ir.ui.view']
        views += create_view("a_")
        root = views[-1]
        views += create_view("b_")
        views += create_view("aa", inherit_id=root.id, mode="primary")
        views += create_view("ab", inherit_id=root.id)
        target = views[-1]
        views += create_view("aba", inherit_id=target.id)
        views[-1].arch = views[-1].arch.replace('aba', 'a_</div>aba<div>ab')
        views += create_view("abb", inherit_id=target.id, mode="primary")

        self.env['ir.translation'].insert_missing(views._fields['arch_db'], views)
        fr_translations = self.env['ir.translation'].search([
            ('name', '=', 'ir.ui.view,arch_db'), ('res_id', 'in', views.ids), ('lang', '=', 'fr_FR')
        ])
        self.assertEqual(len(fr_translations), len(views) + 2)  # +2 for aba
        for trans in fr_translations:
            trans.value = "%s in fr" % trans.src

        combined_arch = '<div>a_<div>ab</div><div>a_</div>aba<div>ab</div></div>'
        self.assertEqual(target._read_template(target.id), combined_arch)

        # duplicate original report, views will be combined into one
        report.copy_report_and_template()
        copy_view = self.env['ir.ui.view'].search([
            ('key', '=', 'web_studio.test_keep_translations_ab_copy_1'),
        ])
        self.assertEqual(copy_view.arch, combined_arch)

        # translations of combined views have been copied to the new view
        translations = self.env['ir.translation'].search([
            ('name', '=', 'ir.ui.view,arch_db'), ('res_id', '=', copy_view.id), ('lang', '=', 'fr_FR')
        ])
        self.assertEqual(len(translations), 3)
        self.assertEqual(set(translations.mapped('src')), set(['a_', 'ab', 'aba']))

    def test_report_action_translations(self):
        self.env['ir.actions.report'].create({
            'name': 'test report in translations',
            'report_name': 'web_studio.test_report_action_translations',
            'model': 'res.users',
        })
        view = self.env['ir.ui.view'].create({
            'type': 'qweb',
            'name': 'test_report_action_translations_view',
            'key': 'web_studio.test_report_action_translations_view',
            'arch': '<div>hello test</div>',
        })

        model = self.env['ir.model'].search([('model', '=', 'res.users')], limit=1)
        action = self.WebStudioController._get_studio_action_translations(model)

        view_ids = next((leaf[2] for leaf in action['domain'] if leaf[0] == 'res_id'), [])
        self.assertIn(view.id, view_ids)

        translations = self.env['ir.translation'].search_read(action['domain'], ['src'])
        translation = next(trans for trans in translations if trans["src"] == "hello test")
        self.assertTrue(translation, 'report translations should shown in "Translations" action')

    def tearDown(self):
        super(TestReportEditor, self).tearDown()
        _request_stack.pop()
