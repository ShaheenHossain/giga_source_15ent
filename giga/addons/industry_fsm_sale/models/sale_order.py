# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, fields


class SaleOrder(models.Model):
    _inherit = ['sale.order']

    task_id = fields.Many2one('project.task', string="Task", help="Task from which quotation have been created")

class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line']

    def _update_line_quantity(self, values):
        # YTI TODO: This method should only be used to post
        # a message on qty update, or to raise a ValidationError
        # Should be split in master 
        if self.env.context.get('fsm_no_message_post'):
            return
        super(SaleOrderLine, self)._update_line_quantity(values)

    def _timesheet_create_task_prepare_values(self, project):
        res = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        if project.is_fsm:
            res.update({'partner_id': self.order_id.partner_shipping_id.id})
        return res

    def _timesheet_create_project_prepare_values(self):
        """Generate project values"""
        values = super(SaleOrderLine, self)._timesheet_create_project_prepare_values()
        if self.product_id.project_template_id.is_fsm:
            values.pop('sale_line_id', False)
        return values
