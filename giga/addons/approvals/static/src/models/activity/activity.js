/** @giga-module **/

import {
    registerClassPatchModel,
    registerFieldPatchModel,
} from '@mail/model/model_core';
import { one2one } from '@mail/model/model_field';
import { insert, unlinkAll } from '@mail/model/model_field_command';

registerClassPatchModel('mail.activity', 'approvals/static/src/models/activity/activity.js', {
    //----------------------------------------------------------------------
    // Public
    //----------------------------------------------------------------------

    /**
     * @override
     */
    convertData(data) {
        const data2 = this._super(data);
        if ('approver_id' in data && 'approver_status' in data) {
            if (!data.approver_id) {
                data2.approval = unlinkAll();
            } else {
                data2.approval = [
                    insert({ id: data.approver_id, status: data.approver_status }),
                ];
            }
        }
        return data2;
    },
});

registerFieldPatchModel('mail.activity', 'approvals/static/src/models/activity/activity.js', {
    approval: one2one('approvals.approval', {
        inverse: 'activity',
    }),
});
