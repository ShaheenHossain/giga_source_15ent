/** @giga-module alias=account_online_synchronization.giga_fin_connector **/
"use strict";

import { registry } from "@web/core/registry";

const actionRegistry = registry.category('actions');
const { loadJS } = owl.utils;
/* global GigaFin */

function GigaFinConnector(parent, action) {
    const id = action.id;
    let mode = action.params.mode || 'link';
    // Ensure that the proxyMode is valid
    const modeRegexp = /^[a-z0-9-_]+$/i;
    if (!modeRegexp.test(action.params.proxyMode)) {
        return;
    }
    let url = 'https://' + action.params.proxyMode + '.gigafin.com/proxy/v1/gigafin_link';

    loadJS(url)
        .then(function () {
            // Create and open the iframe
            let params = {
                data: action.params,
                proxyMode: action.params.proxyMode,
                onEvent: function (event, data) {
                    let rpcUrl = '/web/dataset/call_kw/account.online.link'
                    switch (event) {
                        case 'close':
                            return;
                        case 'reload':
                            return parent.services.action.doAction({type: 'ir.actions.client', tag: 'reload'});
                        case 'notification':
                            parent.services.notification.add(data.message, data);
                            break;
                        case 'exchange_token':
                            parent.services.rpc(rpcUrl + '/exchange_token', {
                                model: 'account.online.link',
                                method: 'exchange_token',
                                args: [[id], data],
                                kwargs: {}
                            })
                            break;
                        case 'success':
                            mode = data.mode || mode;
                            return parent.services.rpc(rpcUrl + '/success', {
                                model: 'account.online.link',
                                method: 'success',
                                args: [[id], mode, data],
                                kwargs: {}
                            })
                            .then(action => parent.services.action.doAction(action));
                        default:
                            return;
                    }
                },
                onAddBank: function () {
                    // If the user doesn't find his bank
                    return parent.services.rpc("/web/dataset/call_kw/account.online.link/create_new_bank_account_action", {
                        model: 'account.online.link',
                        method: 'create_new_bank_account_action',
                        args: [],
                        kwargs: {}
                    })
                    .then(action => parent.services.action.doAction(action, {replace_last_action: true}));
                }
            }
            GigaFin.create(params);
            GigaFin.open();
        });
    return;
}

actionRegistry.add('giga_fin_connector', GigaFinConnector);

export default GigaFinConnector;
