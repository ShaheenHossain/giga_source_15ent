# -*- coding: utf-8 -*-
# Part of Giga Source ERP. See LICENSE file for full copyright and licensing details.

from giga import models, _
from giga.fields import Datetime


class MailingTrace(models.Model):
    _inherit = 'mailing.trace'

    def set_failed(self, domain=None, failure_type=None):
        traces = super(MailingTrace, self).set_failed(domain=domain, failure_type=failure_type)
        traces.marketing_trace_id.write({
            'state': 'error',
            'schedule_date': Datetime.now(),
            'state_msg': _('SMS failed')
        })
        return traces

    def set_clicked(self, domain=None):
        traces = super(MailingTrace, self).set_clicked(domain=domain)
        marketing_sms_traces = traces.filtered(lambda trace: trace.marketing_trace_id and trace.marketing_trace_id.activity_type == 'sms')
        for marketing_trace in marketing_sms_traces.marketing_trace_id:
            marketing_trace.process_event('sms_click')
        return traces

    def set_bounced(self, domain=None):
        traces = super(MailingTrace, self).set_bounced(domain=domain)
        marketing_sms_traces = traces.filtered(lambda trace: trace.marketing_trace_id and trace.marketing_trace_id.activity_type == 'sms')
        for marketing_trace in marketing_sms_traces.marketing_trace_id:
            marketing_trace.process_event('sms_bounce')
        return traces
