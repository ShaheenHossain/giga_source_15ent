# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import api, models, fields, _


class L10nBeScheduleChangeAllocation(models.Model):
    _name = 'l10n_be.schedule.change.allocation'
    _description = 'Update allocation on schedule change'

    effective_date = fields.Date(required=True)
    contract_id = fields.Many2one(
        'hr.contract',
        required=True,
        ondelete='cascade',
    )
    leave_allocation_id = fields.Many2one(
        'hr.leave.allocation',
        required=True,
        ondelete='cascade',
    )
    current_resource_calendar_id = fields.Many2one(
        'resource.calendar',
        required=True,
        ondelete='cascade',
    )
    new_resource_calendar_id = fields.Many2one(
        'resource.calendar',
        required=True,
        ondelete='cascade',
    )

    def apply_directly(self):
        for record in self:
            # Avoid updating the number of days if the contract has been cancelled
            # Contrat may not be open already, it depends on another cron
            if record.contract_id.state in ['draft', 'open']:
                number_of_days = self.env['l10n_be.hr.payroll.schedule.change.wizard']._compute_new_allocation(
                    record.leave_allocation_id, record.current_resource_calendar_id,
                    record.new_resource_calendar_id,
                )
                record.leave_allocation_id.write({
                    'number_of_days': number_of_days,
                })
                record.leave_allocation_id._message_log(body=_('New working schedule on %(contract_name)s.<br/>'
                'New total : %(days)s') % {'contract_name': record.contract_id.name, 'days': number_of_days})

    @api.model
    def _cron_update_allocation_from_new_schedule(self, date=None):
        if not date:
            date = fields.Date.today()
        to_apply = self.search([('effective_date', '<=', date.strftime('%Y-%m-%d'))])
        to_apply.apply_directly()
        to_apply.unlink()
