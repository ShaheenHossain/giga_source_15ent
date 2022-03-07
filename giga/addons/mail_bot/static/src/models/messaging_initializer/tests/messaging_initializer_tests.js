/** @giga-module **/

import { afterEach, beforeEach, start } from '@mail/utils/test_utils';

QUnit.module('mail_bot', {}, function () {
QUnit.module('models', {}, function () {
QUnit.module('messaging_initializer', {}, function () {
QUnit.module('messaging_initializer_tests.js', {
    beforeEach() {
        beforeEach(this);

        this.start = async params => {
            const { env, widget } = await start(Object.assign({}, params, {
                data: this.data,
            }));
            this.env = env;
            this.widget = widget;
        };
    },
    afterEach() {
        afterEach(this);
    },
});


QUnit.test('GigaBot initialized at init', async function (assert) {
    // TODO this test should be completed in combination with
    // implementing _mockMailChannelInitGigaBot task-2300480
    assert.expect(2);

    await this.start({
        env: {
            session: {
                gigabot_initialized: false,
            },
        },
        async mockRPC(route, args) {
            if (args.method === 'init_gigabot') {
                assert.step('init_gigabot');
            }
            return this._super(...arguments);
        },
    });

    assert.verifySteps(
        ['init_gigabot'],
        "should have initialized GigaBot at init"
    );
});

});
});
});
