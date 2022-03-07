/** @giga-module **/

import MockServer from 'web.MockServer';

MockServer.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    async _performRpc(route, args) {
        if (args.model === 'mail.channel' && args.method === 'init_gigabot') {
            return this._mockMailChannelInitGigaBot();
        }
        return this._super(...arguments);
    },

    //--------------------------------------------------------------------------
    // Private Mocked Methods
    //--------------------------------------------------------------------------

    /**
     * Simulates `init_gigabot` on `mail.channel`.
     *
     * @private
     */
    _mockMailChannelInitGigaBot() {
        // TODO implement this mock task-2300480
        // and improve test "GigaBot initialized after 2 minutes"
    },
});
