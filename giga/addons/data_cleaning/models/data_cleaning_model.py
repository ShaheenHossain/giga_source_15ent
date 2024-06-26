# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

import ast
from dateutil.relativedelta import relativedelta
from psycopg2 import sql

from giga import models, api, fields


class DataCleaningModel(models.Model):
    _name = 'data_cleaning.model'
    _description = 'Cleaning Model'
    _order = 'name'

    active = fields.Boolean(default=True)
    name = fields.Char(
        compute='_compute_name', string='Name', readonly=False, store=True, required=True, copy=True)

    res_model_id = fields.Many2one('ir.model', string='Model', required=True, ondelete='cascade')
    res_model_name = fields.Char(
        related='res_model_id.model', string='Model Name', readonly=True, store=True)

    cleaning_mode = fields.Selection([
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ], string='Cleaning Mode', default='manual', required=True)

    rule_ids = fields.One2many('data_cleaning.rule', 'cleaning_model_id', string='Rules')
    records_to_clean_count = fields.Integer('Records To Clean', compute='_compute_records_to_clean')

    # User Notifications for Manual clean
    notify_user_ids = fields.Many2many(
        'res.users', string='Notify Users',
        domain=lambda self: [('groups_id', 'in', self.env.ref('base.group_system').id)],
        default=lambda self: self.env.user,
        help='List of users to notify when there are new records to clean')
    notify_frequency = fields.Integer(string='Notify', default=1)
    notify_frequency_period = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')], string='Notify Frequency Period', default='weeks')
    last_notification = fields.Datetime(readonly=True)

    _sql_constraints = [
        ('check_notif_freq', 'CHECK(notify_frequency > 0)', 'The notification frequency should be greater than 0'),
    ]

    @api.onchange('res_model_id')
    def _compute_name(self):
        for cm_model in self:
            if not cm_model.name:
                cm_model.name = cm_model.res_model_id.name if cm_model.res_model_id else ''

    @api.onchange('res_model_id')
    def _onchange_res_model_id(self):
        self.ensure_one()
        if any(rule.field_id.model_id != self.res_model_id for rule in self.rule_ids):
            self.rule_ids = [(5, 0, 0)]

    def _compute_records_to_clean(self):
        count_data = self.env['data_cleaning.record'].read_group(
            [('cleaning_model_id', 'in', self.ids)],
            ['cleaning_model_id'],
            ['cleaning_model_id'])
        counts = {cd['cleaning_model_id'][0]: cd['cleaning_model_id_count'] for cd in count_data}
        for cm_model in self:
            cm_model.records_to_clean_count = counts[cm_model.id] if cm_model.id in counts else 0

    def _cron_clean_records(self):
        self.sudo().search([])._clean_records()
        self.sudo()._notify_records_to_clean()

    def _clean_records_format_phone(self, actions, field):
        self.ensure_one()

        self._cr.execute("""
            SELECT res_id, data_cleaning_rule_id
            FROM data_cleaning_record
            JOIN data_cleaning_record_data_cleaning_rule_rel
            ON data_cleaning_record_data_cleaning_rule_rel.data_cleaning_record_id = data_cleaning_record.id""")
        existing_rows = self._cr.fetchall()

        records = self.env[self.res_model_name].search([(field, 'not in', [False, ''])])
        field_id = actions[field]['field_id']
        rule_ids = actions[field]['rule_ids']
        result = []
        for record in records:
            record_country = self.env['data_cleaning.record']._get_country_id(record)
            formatted = self.env['data_cleaning.record']._phone_format(record[field], record_country)
            if (record.id, rule_ids[0]) not in existing_rows and formatted and record[field] != formatted:
                result.append({
                    'res_id': record['id'],
                    'rule_ids': rule_ids,
                    'cleaning_model_id': self.id,
                    'field_id': field_id,
                })
        return result


    def _clean_records(self):
        self.flush()

        records_to_clean = []
        for cleaning_model in self:
            records_to_create = []
            actions = cleaning_model.rule_ids._action_to_sql()
            for field in actions:
                action = actions[field]['action']
                field_id = actions[field]['field_id']
                rule_ids = actions[field]['rule_ids']
                operator = actions[field]['operator']
                cleaner = getattr(cleaning_model, '_clean_records_%s' % action, None)
                if cleaner:
                    values = cleaner(actions, field)
                    records_to_create += values
                else:
                    active_name = self.env[cleaning_model.res_model_name]._active_name
                    active_cond = sql.SQL("AND {}").format(sql.Identifier(active_name)) if active_name else sql.SQL('')

                    query = sql.SQL("""
                        SELECT
                            id AS res_id
                        FROM
                            {table}
                        WHERE
                            {field_name} {operator} {cleaned_field_expr}
                            AND NOT EXISTS(
                                SELECT 1
                                FROM {cleaning_record_table}
                                WHERE
                                    res_id = {table}.id
                                    AND cleaning_model_id = %s)
                            {active_cond}
                    """).format(
                        table=sql.Identifier(self.env[cleaning_model.res_model_name]._table),
                        field_name=sql.Identifier(field),
                        operator=sql.SQL(operator),
                        # can be complex sql expression & multiple actions get
                        # combined through string formatting, so doesn't seem
                        # to be a smarter solution than whitelisting the entire thing
                        cleaned_field_expr=sql.SQL(action.format(field)),
                        cleaning_record_table=sql.Identifier(self.env['data_cleaning.record']._table),
                        active_cond=active_cond
                    )
                    self._cr.execute(query, [cleaning_model.id])
                    for r in self._cr.fetchall():
                        records_to_create.append({
                            'res_id': r[0],
                            'rule_ids': rule_ids,
                            'cleaning_model_id': cleaning_model.id,
                            'field_id': field_id,
                        })

            if cleaning_model.cleaning_mode == 'automatic':
                self.env['data_cleaning.record'].create(records_to_create).action_validate()
            else:
                records_to_clean = records_to_clean + records_to_create
        self.env['data_cleaning.record'].create(records_to_clean)

    @api.model
    def _notify_records_to_clean(self):
        for cleaning_model in self.search([('cleaning_mode', '=', 'manual')]):
            if not cleaning_model.notify_user_ids or not cleaning_model.notify_frequency:
                continue

            if cleaning_model.notify_frequency_period == 'days':
                delta = relativedelta(day=cleaning_model.notify_frequency)
            elif cleaning_model.notify_frequency_period == 'weeks':
                delta = relativedelta(weeks=cleaning_model.notify_frequency)
            else:
                delta = relativedelta(months=cleaning_model.notify_frequency)

            if not cleaning_model.last_notification or\
                    (cleaning_model.last_notification + delta) < fields.Datetime.now():
                cleaning_model.last_notification = fields.Datetime.now()
                cleaning_model._send_notification(delta)

    def _send_notification(self, delta):
        self.ensure_one()
        last_date = fields.Date.today() - delta
        records_count = self.env['data_cleaning.record'].search_count([
            ('cleaning_model_id', '=', self.id),
            ('create_date', '>=', last_date)
        ])

        if records_count:
            partner_ids = self.notify_user_ids.partner_id.ids
            template = self.env.ref('data_cleaning.notification')
            menu_id = self.env.ref('data_cleaning.menu_data_cleaning_root').id
            kwargs = {
                'body': template._render(dict(records_count=records_count, res_model_label=self.res_model_id.name, cleaning_model_id=self.id, menu_id=menu_id)),
                'partner_ids': partner_ids,
            }
            self.env['mail.thread'].with_context(mail_notify_author=True).message_notify(**kwargs)

    ############
    # Overrides
    ############
    def write(self, vals):
        if 'active' in vals and not vals['active']:
            self.env['data_cleaning.record'].search([('cleaning_model_id', 'in', self.ids)]).unlink()
        super(DataCleaningModel, self).write(vals)

    ##########
    # Actions
    ##########
    def open_records(self):
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id("data_cleaning.action_data_cleaning_record")
        action['context'] = dict(ast.literal_eval(action.get('context')), searchpanel_default_cleaning_model_id=self.id)
        return action

    def action_clean_records(self):
        self.sudo()._clean_records()

        if self.cleaning_mode == 'manual':
            return self.open_records()
