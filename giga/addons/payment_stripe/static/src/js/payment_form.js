/* global Stripe */
giga.define('payment_stripe.payment_form', require => {
    'use strict';

    const checkoutForm = require('payment.checkout_form');
    const manageForm = require('payment.manage_form');

    const stripeMixin = {

        /**
         * Redirect the customer to Stripe hosted payment page.
         *
         * @override method from payment.payment_form_mixin
         * @private
         * @param {string} provider - The provider of the payment option's acquirer
         * @param {number} paymentOptionId - The id of the payment option handling the transaction
         * @param {object} processingValues - The processing values of the transaction
         * @return {undefined}
         */
        _processRedirectPayment: function (provider, paymentOptionId, processingValues) {
            if (provider !== 'stripe') {
                return this._super(...arguments);
            }

            const stripeJS = Stripe(processingValues['publishable_key']);
            stripeJS.redirectToCheckout({
                sessionId: processingValues['session_id']
            });
        },

    };

    checkoutForm.include(stripeMixin);
    manageForm.include(stripeMixin);

});
