giga.define('social_test_full.test_formatter_regex', function (require) {
"use strict";

var SocialPostFormatterMixin = require('social.post_formatter_mixin');

QUnit.module('Social Formatter Regex', {}, () => {
    QUnit.test('Facebook Message', (assert) => {
        assert.expect(1);

        SocialPostFormatterMixin._getMediaType = () => 'facebook';
        SocialPostFormatterMixin.accountId = 42;

        const testMessage = 'Hello @[542132] Giga-Social, check this out: https://www.gigasource.de #crazydeals #giga';
        const finalMessage = SocialPostFormatterMixin._formatPost(testMessage);

        assert.equal(finalMessage, [
            "Hello",
            "<a href='/social_facebook/redirect_to_profile/42/542132?name=Giga-Social' target='_blank'>Giga-Social</a>,",
            "check this out:",
            "<a href='https://www.gigasource.de' target='_blank' rel='noreferrer noopener'>https://www.gigasource.de</a>",
            "<a href='https://www.facebook.com/hashtag/crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.facebook.com/hashtag/giga' target='_blank'>#giga</a>",
        ].join(' '));
    });

    QUnit.test('Instagram Message', (assert) => {
        assert.expect(1);

        SocialPostFormatterMixin._getMediaType = () => 'instagram';

        const testMessage = 'Hello @Giga-Social, check this out: https://www.gigasource.de #crazydeals #giga';
        const finalMessage = SocialPostFormatterMixin._formatPost(testMessage);

        assert.equal(finalMessage, [
            "Hello",
            "<a href='https://www.instagram.com/Giga-Social' target='_blank'>@Giga-Social</a>,",
            "check this out:",
            "<a href='https://www.gigasource.de' target='_blank' rel='noreferrer noopener'>https://www.gigasource.de</a>",
            "<a href='https://www.instagram.com/explore/tags/crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.instagram.com/explore/tags/giga' target='_blank'>#giga</a>",
        ].join(' '));
    });

    QUnit.test('LinkedIn Message', (assert) => {
        assert.expect(1);

        SocialPostFormatterMixin._getMediaType = () => 'linkedin';

        const testMessage = 'Hello, check this out: https://www.gigasource.de #crazydeals #giga';
        const finalMessage = SocialPostFormatterMixin._formatPost(testMessage);

        assert.equal(finalMessage, [
            "Hello, check this out:",
            "<a href='https://www.gigasource.de' target='_blank' rel='noreferrer noopener'>https://www.gigasource.de</a>",
            "<a href='https://www.linkedin.com/feed/hashtag/crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.linkedin.com/feed/hashtag/giga' target='_blank'>#giga</a>",
        ].join(' '));
    });

    QUnit.test('Twitter Message', (assert) => {
        assert.expect(1);

        SocialPostFormatterMixin._getMediaType = () => 'twitter';

        const testMessage = 'Hello @Giga-Social, check this out: https://www.gigasource.de #crazydeals #giga';
        const finalMessage = SocialPostFormatterMixin._formatPost(testMessage);

        assert.equal(finalMessage, [
            "Hello",
            "<a href='https://twitter.com/Giga-Social' target='_blank'>@Giga-Social</a>,",
            "check this out:",
            "<a href='https://www.gigasource.de' target='_blank' rel='noreferrer noopener'>https://www.gigasource.de</a>",
            "<a href='https://twitter.com/hashtag/crazydeals?src=hash' target='_blank'>#crazydeals</a>",
            "<a href='https://twitter.com/hashtag/giga?src=hash' target='_blank'>#giga</a>",
        ].join(' '));
    });

    QUnit.test('YouTube Message', (assert) => {
        assert.expect(1);

        SocialPostFormatterMixin._getMediaType = () => 'youtube';

        const testMessage = 'Hello, check this out: https://www.gigasource.de #crazydeals #giga';
        const finalMessage = SocialPostFormatterMixin._formatPost(testMessage);

        assert.equal(finalMessage, [
            "Hello, check this out:",
            "<a href='https://www.gigasource.de' target='_blank' rel='noreferrer noopener'>https://www.gigasource.de</a>",
            "<a href='https://www.youtube.com/results?search_query=%23crazydeals' target='_blank'>#crazydeals</a>",
            "<a href='https://www.youtube.com/results?search_query=%23giga' target='_blank'>#giga</a>",
        ].join(' '));
    });
});

});
