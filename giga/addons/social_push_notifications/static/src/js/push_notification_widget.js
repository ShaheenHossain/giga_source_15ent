/* global firebase */
giga.define('social_push_notifications.NotificationManager', function (require) {
"use strict";

var core = require('web.core');
var publicWidget = require('web.public.widget');
var utils = require('web.utils');
var localStorage = require('web.local_storage');
var NotificationRequestPopup = require('social_push_notifications.NotificationRequestPopup');

publicWidget.registry.NotificationWidget =  publicWidget.Widget.extend({
    selector: '#wrapwrap',

    /**
     * This will start listening to notifications if permission was already granted
     * by the user or ask for permission after a timeout (configurable) and then start listening.
     *
     * @override
     */
    start: function () {
        var self = this;
        var superPromise = this._super.apply(this, arguments);

        if (!this._isBrowserCompatible()) {
            return superPromise;
        }

        if (Notification.permission === "granted") {
            if (!this._isConfigurationUpToDate()) {
                this._fetchPushConfiguration().then(function (config) {
                    self._registerServiceWorker(config);
                });
            }
        } else if (Notification.permission !== "denied") {
            this._askPermission();
        }
        core.bus.on('open_notification_request', this, this._onNotificationRequest);

        return superPromise;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Will check browser compatibility before trying to register the service worker.
     * Browsers compatible now (11/07/2019):
     * - Chrome
     * - Firefox
     * - Edge
     *
     * For Safari we would need to use an entirely different service since they have their own
     * push notifications mechanism.
     * See: https://developer.apple.com/notifications/safari-push-notifications/
     *
     * @private
     */
    _isBrowserCompatible: function () {
        if (!('serviceWorker' in navigator)) {
            // Service Worker isn't supported on this browser
            return false;
        }

        if (!('PushManager' in window)) {
            // Push isn't supported on this browser
            return false;
        }

        return true;
    },

    /**
     * Will register a service worker to display later notifications.
     * This method also handles the notification "subscription token".
     *
     * The token will be used by firebase to notify this user directly.
     *
     * @private
     */
    _registerServiceWorker: function (config) {
        var self = this;

        if (!config.firebase_push_certificate_key
            || !config.firebase_project_id
            || !config.firebase_web_api_key) {
            // missing configuration
            return;
        }

        firebase.initializeApp({
            apiKey: config.firebase_web_api_key,
            projectId: config.firebase_project_id,
            messagingSenderId: config.firebase_sender_id
        });

        var messaging = firebase.messaging();
        var baseWorkerUrl = '/social_push_notifications/static/src/js/push_service_worker.js';
        navigator.serviceWorker.register(baseWorkerUrl + '?senderId=' + config.firebase_sender_id)
            .then(function (registration) {
                messaging.useServiceWorker(registration);
                messaging.usePublicVapidKey(config.firebase_push_certificate_key);
                messaging.getToken().then(function (token) {
                    self._registerToken(token);
                });
        });
    },

    /**
     * Checks that the push notification configuration is still up to date.
     * (It expires after 7 days)
     *
     * @private
     */
    _isConfigurationUpToDate: function () {
        var pushConfiguration = this._getNotificationRequestConfiguration();
        if (pushConfiguration) {
            if (new Date() < new Date(pushConfiguration.expirationDate)) {
                return true;
            }
        }

        return false;
    },

    /**
     * Responsible for fetching the full push configuration.
     *
     * When the configuration is fetched, it's stored into local storage (for 7 days)
     * to save future requests.
     *
     * @private
     */
    _fetchPushConfiguration: function () {
        var fetchPromise = this._rpc({
            route: '/social_push_notifications/fetch_push_configuration'
        });

        fetchPromise.then(function (config) {
            var expirationDate = new Date();
            expirationDate.setDate(expirationDate.getDate() + 7);
            localStorage.setItem('social_push_notifications.notification_request_config',
                JSON.stringify({
                    'title': config.notification_request_title,
                    'body': config.notification_request_body,
                    'delay': config.notification_request_delay,
                    'icon': config.notification_request_icon,
                    'expirationDate': expirationDate
            }));
        });

        return fetchPromise;
    },

    /**
     * Will register the subscription token into database for later notifications
     *
     * We store the token in the localStorage for 7 days to avoid having to save
     * it every time the user loads a website page.
     *
     * If the token from localStorage is different from the one we are registering, we clean
     * the old one from the registrations.
     *
     * @param {string} token
     */
    _registerToken: function (token) {
        this;

        var pushConfiguration = this._getPushConfiguration();
        if (pushConfiguration && pushConfiguration.token !== token) {
            this._rpc({
                route: '/social_push_notifications/unregister',
                params: {
                    token: pushConfiguration.token
                }
            });
        }

        this._rpc({
            route: '/social_push_notifications/register',
            params: {
                token: token
            }
        }).then(function (res) {
            // If new visitor has been created, store signature in cookie.
            if (res && res.visitor_uuid) {
                utils.set_cookie('visitor_uuid', res.visitor_uuid);
            }

            localStorage.setItem('social_push_notifications.configuration', JSON.stringify({
                'token': token,
            }));
        });
    },

    /**
     * We work with 2 different permission request popups:
     *
     * - The first one is a regular bootstrap popup configurable (title,text,...) from the backend.
     *   It has an accept and a deny buttons. It also closes if the user clicks outside.
     *
     * -> if closed by clicking outside/on cross, will re-open on next page reload
     * -> if closed by clicking 'Deny', will re-open after 7 days on page reload
     * -> if closed by clicking on 'Allow', triggers the second popup.
     *
     * - The second popup is the one opened by the browser when asking for notifications permission.
     *
     * -> if closed by clicking outside/on cross, will re-open the first popup on next page reload
     * -> if closed by clicking on 'Block', we will not be allowed to send notifications to that user.
     *    (TODO awa: give some kind of feedback and show how to go to page settings?
     *     -> might be tricky, probably need a full spec later)
     * -> if closed by clicking on 'Allow', we register a service worker to send notifications.
     *
     * In addition to that, the first popup configuration (title,text,...) is stored into localStorage
     * to avoid having to fetch it on every page reload if the user doesn't accept or deny the popup.
     *
     * The configuration is stored for 7 days to still receive visual updates if the configuration
     * changes on the backend side.
     * 
     * @param {String} [nextAskPermissionKeySuffix] optional - Suffix of the cache entry
     * @param {Object} [forcedPopupConfig] optional - Properties that will overwrite the notification request configuration.
     * @param {String} forcedPopupConfig.title optional - Title of the popup.
     * @param {String} forcedPopupConfig.body optional - Body of the popup.
     * @param {String} forcedPopupConfig.delay optional - Delay of the popup.
     * @param {String} forcedPopupConfig.icon optional - Icon of the popup.
     */
    _askPermission: async function (nextAskPermissionKeySuffix, forcedPopupConfig) {
        var self = this;

        var nextAskPermission = localStorage.getItem('social_push_notifications.next_ask_permission' +
            (nextAskPermissionKeySuffix ? '.' + nextAskPermissionKeySuffix : ''));
        if (nextAskPermission && new Date() < new Date(nextAskPermission)) {
            return;
        }

        var pushConfig = null;
        var popupConfig = this._getNotificationRequestConfiguration();

        if (!popupConfig || new Date() > new Date(popupConfig.expirationDate)) {
            pushConfig = await this._fetchPushConfiguration();
            popupConfig = {
                title: pushConfig.notification_request_title,
                body: pushConfig.notification_request_body,
                delay: pushConfig.notification_request_delay,
                icon: pushConfig.notification_request_icon
            };
        }
        if (!popupConfig || !popupConfig.title || !popupConfig.body) {
            return; // this means that the web push notifications are not enabled in the settings
        }
        if (forcedPopupConfig) {
            popupConfig = _.extend({}, popupConfig, forcedPopupConfig);
        }
        self._showNotificationRequestPopup(popupConfig, pushConfig, nextAskPermissionKeySuffix);
    },

    /**
     * Method responsible for the display of the Notification Request Popup.
     * It also reacts the its 'allow' and 'deny' events (see '_askPermission' for details).
     *
     * @param {Object} popupConfig the popup configuration (title,body,...)
     * @param {Object} [pushConfig] optional, will be fetched if absent
     * @param {String} [nextAskPermissionKeySuffix] optional
     */
    _showNotificationRequestPopup: function (popupConfig, pushConfig, nextAskPermissionKeySuffix) {
        var selector = '.o_social_push_notifications_permission_request';
        if (!popupConfig.title || !popupConfig.body || this.$el.find(selector).length > 0) {
            return;
        }

        var self = this;
        var notificationRequestPopup = new NotificationRequestPopup(this, {
            title: popupConfig.title,
            body: popupConfig.body,
            delay: popupConfig.delay,
            icon: popupConfig.icon
        });
        notificationRequestPopup.appendTo(this.$el);

        notificationRequestPopup.on('allow', null, function () {
            Notification.requestPermission().then(function () {
                if (Notification.permission === "granted") {
                    if (pushConfig) {
                        self._registerServiceWorker(pushConfig);
                    } else {
                        self._fetchPushConfiguration().then(function (config) {
                            self._registerServiceWorker(config);
                        });
                    }
                }
            });
        });

        notificationRequestPopup.on('deny', null, function () {
            var nextAskPermissionDate = new Date();
            nextAskPermissionDate.setDate(nextAskPermissionDate.getDate() + 7);
            localStorage.setItem('social_push_notifications.next_ask_permission' +
                (nextAskPermissionKeySuffix ? '.' + nextAskPermissionKeySuffix : ''),
                nextAskPermissionDate);
        });
    },

    _getPushConfiguration: function () {
        return this._getJSONLocalStorageItem(
            'social_push_notifications.configuration'
        );
    },

    _getNotificationRequestConfiguration: function () {
        return this._getJSONLocalStorageItem(
            'social_push_notifications.notification_request_config'
        );
    },

    _getJSONLocalStorageItem: function (key) {
        var value = localStorage.getItem(key);
        if (value) {
            return JSON.parse(value);
        }

        return null;
    },

    /**
     * The module will guarantee that no other push notification request for
     * the `nextAskPermissionKeySuffix` key will issued if the user dismissed
     * a request using the same key within the last 7 days.
     * 
     * This can be useful in specific context, e.g:
     * When favoriting event.tracks, we want to re-ask the user to enable the push
     * notifications even if the user recently dismisses the default one. By
     * using a custom key, we can issue a new request without having to wait that
     * the 7 days restriction set by the first request expires. When the user
     * dismisses the new request, a 7 days restriction will also be applied to the
     * provided key.
     * 
     * @param {String} [nextAskPermissionKeySuffix] Suffix of the cache entry.
     * @param {Object} [forcedPopupConfig] Properties of the popup.
     * @param {String} forcedPopupConfig.title optional - Title of the popup.
     * @param {String} forcedPopupConfig.body optional - Body of the popup.
     * @param {String} forcedPopupConfig.delay optional - Delay of the popup.
     * @param {String} forcedPopupConfig.icon optional - Icon of the popup.
     */
    _onNotificationRequest: async function (nextAskPermissionKeySuffix, forcedPopupConfig) {
        if (Notification.permission !== 'default') {
            return;
        }
        this._askPermission(nextAskPermissionKeySuffix, forcedPopupConfig);
    },
});

return publicWidget.registry.NotificationWidget;

});
