# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    allow_material = fields.Boolean("Products on Tasks", compute="_compute_allow_material", store=True, readonly=False)
    allow_quotations = fields.Boolean(
        "Extra Quotations", compute="_compute_allow_quotations", store=True, readonly=False)
    allow_billable = fields.Boolean(store=True, readonly=False, compute='_compute_allow_billable')
    sale_line_id = fields.Many2one(compute="_compute_sale_line_id", store=True, readonly=False)

    _sql_constraints = [
        ('material_imply_billable', "CHECK((allow_material = 't' AND allow_billable = 't') OR (allow_material = 'f'))", 'The material can be allowed only when the task can be billed.'),
        ('fsm_imply_task_rate', "CHECK((is_fsm = 't' AND sale_line_id IS NULL) OR (is_fsm = 'f'))", 'An FSM project must be billed at task rate or employee rate.'),
        ('timesheet_product_required_if_billable_and_timesheets_and_fsm_projects', """
            CHECK(
                (allow_billable = 't' AND allow_timesheets = 't' AND is_fsm = 't' AND timesheet_product_id IS NOT NULL)
                OR (allow_billable IS NOT TRUE)
                OR (allow_timesheets IS NOT TRUE)
                OR (is_fsm IS NOT TRUE)
                OR (allow_billable IS NULL)
                OR (allow_timesheets IS NULL)
                OR (is_fsm IS NULL)
            )""", 'The timesheet product is required when the fsm project can be billed and timesheets are allowed.'),
    ]

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if 'allow_quotations' in fields_list and 'allow_quotations' not in defaults and defaults.get('is_fsm'):
            defaults['allow_quotations'] = self.env.user.has_group('industry_fsm.group_fsm_quotation_from_task')
        return defaults

    @api.depends('is_fsm')
    def _compute_allow_quotations(self):
        if not self.env.user.has_group('industry_fsm.group_fsm_quotation_from_task'):
            self.allow_quotations = False
        else:
            for project in self:
                project.allow_quotations = project.is_fsm

    @api.depends('is_fsm')
    def _compute_allow_billable(self):
        fsm_projects = self.filtered('is_fsm')
        fsm_projects.allow_billable = True

    @api.depends('allow_billable', 'is_fsm')
    def _compute_allow_material(self):
        for project in self:
            if not project._origin:
                project.allow_material = project.is_fsm and project.allow_billable
            else:
                project.allow_material = project.allow_billable

    def flush(self, fnames=None, records=None):
        if fnames is not None:
            # force 'allow_billable' and 'allow_material' to be flushed
            # altogether in order to satisfy the SQL constraint above
            fnames = set(fnames)
            if 'allow_billable' in fnames or 'allow_material' in fnames:
                fnames.add('allow_billable')
                fnames.add('allow_material')
        return super().flush(fnames, records)

    @api.depends('sale_line_id', 'sale_line_employee_ids', 'allow_billable', 'is_fsm')
    def _compute_pricing_type(self):
        fsm_projects = self.filtered(lambda project: project.allow_billable and project.is_fsm)
        for fsm_project in fsm_projects:
            if fsm_project.sale_line_employee_ids:
                fsm_project.update({'pricing_type': 'employee_rate'})
            else:
                fsm_project.update({'pricing_type': 'task_rate'})
        super(Project, self - fsm_projects)._compute_pricing_type()

    @api.depends('is_fsm')
    def _compute_sale_line_id(self):
        # We cannot have a SOL in the fsm project
        fsm_projects = self.filtered('is_fsm')
        fsm_projects.update({'sale_line_id': False})
        super(Project, self - fsm_projects)._compute_sale_line_id()

    @api.depends('partner_id', 'pricing_type', 'is_fsm')
    def _compute_display_create_order(self):
        fsm_projects = self.filtered('is_fsm')
        fsm_projects.update({'display_create_order': False})
        super(Project, self - fsm_projects)._compute_display_create_order()

    @api.depends('sale_line_employee_ids.sale_line_id', 'sale_line_id')
    def _compute_partner_id(self):
        basic_projects = self.filtered(lambda project: not project.is_fsm)
        super(Project, basic_projects)._compute_partner_id()
