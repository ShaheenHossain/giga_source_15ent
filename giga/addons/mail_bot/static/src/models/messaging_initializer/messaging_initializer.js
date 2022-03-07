/** @giga-module **/

import { registerInstancePatchModel } from '@mail/model/model_core';

registerInstancePatchModel('mail.messaging_initializer', 'mail_bot/static/src/models/messaging_initializer/messaging_initializer.js', {
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    async _initializeGigaBot() {
        const data = await this.async(() => this.env.services.rpc({
            model: 'mail.channel',
            method: 'init_gigabot',
        }));
        if (!data) {
            return;
        }
        this.env.session.gigabot_initialized = true;
    },

    /**
     * @override
     */
    async start() {
        await this.async(() => this._super());

        if ('gigabot_initialized' in this.env.session && !this.env.session.gigabot_initialized) {
            this._initializeGigaBot();
        }
    },
});
