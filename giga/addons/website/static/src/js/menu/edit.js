giga.define('website.editMenu', function (require) {
'use strict';

var core = require('web.core');
var dom = require('web.dom');
var wysiwygLoader = require('web_editor.loader');
var websiteNavbarData = require('website.navbar');
var Dialog = require('web.Dialog');

const { registry } = require("@web/core/registry");

var _t = core._t;

/**
 * Adds the behavior when clicking on the 'edit' button (+ editor interaction)
 */
var EditPageMenu = websiteNavbarData.WebsiteNavbarActionWidget.extend({
    assetLibs: ['web_editor.compiled_assets_wysiwyg', 'website.compiled_assets_wysiwyg'],

    xmlDependencies: ['/website/static/src/xml/website.editor.xml'],
    actions: _.extend({}, websiteNavbarData.WebsiteNavbarActionWidget.prototype.actions, {
        edit: '_startEditMode',
        on_save: '_onSave',
    }),
    custom_events: _.extend({}, websiteNavbarData.WebsiteNavbarActionWidget.custom_events || {}, {
        content_will_be_destroyed: '_onContentWillBeDestroyed',
        content_was_recreated: '_onContentWasRecreated',
        snippet_will_be_cloned: '_onSnippetWillBeCloned',
        snippet_cloned: '_onSnippetCloned',
        snippet_dropped: '_onSnippetDropped',
        snippet_removed: '_onSnippetRemoved',
        edition_will_stopped: '_onEditionWillStop',
        edition_was_stopped: '_onEditionWasStopped',
        request_save: '_onSnippetRequestSave',
        request_cancel: '_onSnippetRequestCancel',
    }),

    /**
     * @constructor
     */
    init: function (parent, options = {}) {
        this._super.apply(this, arguments);
        this.options = options;
        this.wysiwygOptions = options.wysiwygOptions || {};
        var context;
        this.trigger_up('context_get', {
            extra: true,
            callback: function (ctx) {
                context = ctx;
            },
        });
        this.oeStructureSelector = '#wrapwrap .oe_structure[data-oe-xpath][data-oe-id]';
        this.oeFieldSelector = '#wrapwrap [data-oe-field]';
        this.oeCoverSelector = '#wrapwrap [data-res-model][data-name="Cover"]';
        if (options.savableSelector) {
            this.savableSelector = options.savableSelector;
        } else {
            this.savableSelector = `${this.oeStructureSelector}, ${this.oeFieldSelector}, ${this.oeCoverSelector}`;
        }
        this.editableFromEditorMenu = options.editableFromEditorMenu || this.editableFromEditorMenu;
        this._editorAutoStart = (context.editable && window.location.search.indexOf('enable_editor') >= 0);
        var url = new URL(window.location.href);
        url.searchParams.delete('enable_editor');
        url.searchParams.delete('with_loader');
        window.history.replaceState({}, null, url);
    },
    /**
     * Auto-starts the editor if necessary or add the welcome message otherwise.
     *
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);

        // If we auto start the editor, do not show a welcome message
        if (this._editorAutoStart) {
            return Promise.all([def, this._startEditMode()]);
        }

        // Check that the page is empty
        var $wrap = this._targetForEdition().filter('#wrapwrap.homepage').find('#wrap');

        if ($wrap.length && $wrap.html().trim() === '') {
            // If readonly empty page, show the welcome message
            this.$welcomeMessage = $(core.qweb.render('website.homepage_editor_welcome_message'));
            this.$welcomeMessage.addClass('o_homepage_editor_welcome_message');
            this.$welcomeMessage.css('min-height', $wrap.parent('main').height() - ($wrap.outerHeight(true) - $wrap.height()));
            $wrap.empty().append(this.$welcomeMessage);
        }

        return def;
    },

    /**
     * Asks the snippets to clean themself, then saves the page, then reloads it
     * if asked to.
     *
     * @param {boolean} [reload=true]
     *        true if the page has to be reloaded after the save
     * @returns {Promise}
     */
    save: async function (reload = true) {
        if (this._saving) {
            return false;
        }
        this.observer.disconnect();
        var self = this;
        this._saving = true;
        this.trigger_up('edition_will_stopped');
        const destroy = () => {
            self.wysiwyg.destroy();
            self.trigger_up('edition_was_stopped');
            self.destroy();
        };
        if (!this.wysiwyg.isDirty()) {
            return destroy();
        }
        return this.wysiwyg.saveContent(false).then((result) => {
            var $wrapwrap = $('#wrapwrap');
            self.editableFromEditorMenu($wrapwrap).removeClass('o_editable');
            if (reload) {
                // remove top padding because the connected bar is not visible
                $('body').removeClass('o_connected_user');
                return self._reload();
            } else {
                destroy();
            }
            return true;
        }).guardedCatch(() => {
            this._saving = false;
        });
    },
    /**
     * Asks the user if they really wants to discard their changes (if any),
     * then simply reloads the page if they want to.
     *
     * @param {boolean} [reload=true]
     *        true if the page has to be reloaded when the user answers yes
     *        (do nothing otherwise but add this to allow class extension)
     * @returns {Deferred}
     */
    cancel: function (reload = true) {
        var self = this;
        var def = new Promise(function (resolve, reject) {
            if (!self.wysiwyg.isDirty()) {
                resolve();
            } else {
                var confirm = Dialog.confirm(self, _t("If you discard the current edits, all unsaved changes will be lost. You can cancel to return to edit mode."), {
                    confirm_callback: resolve,
                });
                confirm.on('closed', self, reject);
            }
        });

        return def.then(function () {
            self.trigger_up('edition_will_stopped');
            var $wrapwrap = $('#wrapwrap');
            self.editableFromEditorMenu($wrapwrap).removeClass('o_editable');
            if (reload) {
                window.onbeforeunload = null;
                self.wysiwyg.destroy();
                return self._reload();
            } else {
                self.wysiwyg.destroy();
                self.trigger_up('readonly_mode');
                self.trigger_up('edition_was_stopped');
                self.destroy();
            }
        });
    },
    /**
     * Returns the editable areas on the page.
     *
     * @param {DOM} $wrapwrap
     * @returns {jQuery}
     */
    editableFromEditorMenu: function ($wrapwrap) {
        return $wrapwrap.find('[data-oe-model]')
            .not('.o_not_editable')
            .filter(function () {
                var $parent = $(this).closest('.o_editable, .o_not_editable');
                return !$parent.length || $parent.hasClass('o_editable');
            })
            .not('link, script')
            .not('[data-oe-readonly]')
            .not('img[data-oe-field="arch"], br[data-oe-field="arch"], input[data-oe-field="arch"]')
            .not('.oe_snippet_editor')
            .not('hr, br, input, textarea')
            .add('.o_editable');
    },

    //--------------------------------------------------------------------------
    // Actions
    //--------------------------------------------------------------------------

    /**
     * Creates an editor instance and appends it to the DOM. Also remove the
     * welcome message if necessary.
     *
     * @private
     * @returns {Promise}
     */
    _startEditMode: async function () {
        var self = this;
        if (this.editModeEnable) {
            return;
        }
        this.trigger_up('widgets_stop_request', {
            $target: this._targetForEdition(),
        });
        if (this.$welcomeMessage) {
            this.$welcomeMessage.detach(); // detach from the readonly rendering before the clone by wysiwyg.
        }
        this.editModeEnable = true;

        await this._createWysiwyg();

        var res = await new Promise(function (resolve, reject) {
            self.trigger_up('widgets_start_request', {
                editableMode: true,
                onSuccess: resolve,
                onFailure: reject,
            });
        });

        const $loader = $('div.o_theme_install_loader_container');
        if ($loader) {
            $loader.remove();
        }

        return res;
    },
    /**
     * On save, the editor will ask to parent widgets if something needs to be
     * done first. The website navbar will receive that demand and asks to its
     * action-capable components to do something. For example, the content menu
     * handles page-related options saving. However, some users with limited
     * access rights do not have the content menu... but the website navbar
     * expects that the save action is performed. So, this empty action is
     * defined here so that all users have an 'on_save' related action.
     *
     * @private
     * @todo improve the system to somehow declare required/optional actions
     */
    _onSave: function () {},

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    async _createWysiwyg() {
        var $wrapwrap = $('#wrapwrap');
        $wrapwrap.removeClass('o_editable'); // clean the dom before edition
        this.editableFromEditorMenu($wrapwrap).addClass('o_editable');

        this.wysiwyg = await this._wysiwygInstance();

        await this.wysiwyg.attachTo($('#wrapwrap'));
        this.trigger_up('edit_mode');
        this.$el.css({width: ''});

        // Only make the giga structure and fields editable.
        this.wysiwyg.gigaEditor.observerUnactive();
        $('#wrapwrap').on('click.giga-website-editor', '*', this, this._preventDefault);
        this._addEditorMessages(); // Insert editor messages in the DOM without observing.
        if (this.options.beforeEditorActive) {
            this.options.beforeEditorActive();
        }
        this.wysiwyg.gigaEditor.observerActive();

        // 1. Make sure every .o_not_editable is not editable.
        // 2. Observe changes to mark dirty structures and fields.
        this.observer = new MutationObserver(records => {
            this.wysiwyg.gigaEditor.observerUnactive();
            $('#wrap').find('.o_not_editable[contenteditable!=false]').attr('contenteditable', false);
            this.wysiwyg.gigaEditor.observerActive();

            records = this.wysiwyg.gigaEditor.filterMutationRecords(records);
            // Skip the step for this stack because if the editor undo the first
            // step that has a dirty element, the following code would have
            // generated a new stack and break the "redo" of the editor.
            this.wysiwyg.gigaEditor.automaticStepSkipStack();

            for (const record of records) {
                const $savable = $(record.target).closest(this.savableSelector);

                if (record.attributeName === 'contenteditable') {
                    continue;
                }
                $savable.not('.o_dirty').each(function () {
                    const $el = $(this);
                    if (!$el.closest('[data-oe-readonly]').length) {
                        $el.addClass('o_dirty');
                    }
                });
            }
        });

        this.observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeOldValue: true,
            characterData: true,
        });
        $('body').addClass('editor_started');
    },

    _getContentEditableAreas () {
        return $(this.savableSelector).not('input, [data-oe-readonly],[data-oe-type="monetary"],[data-oe-many2one-id], [data-oe-field="arch"]:empty').filter((_, el) => {
            return !$(el).closest('.o_not_editable').length;
        }).toArray();
    },
    /**
     * Call preventDefault of an event.
     *
     * @private
     */
    _preventDefault(e) {
        e.preventDefault();
    },
    /**
     * Adds automatic editor messages on drag&drop zone elements.
     *
     * @private
     */
    _addEditorMessages: function () {
        const $editable = this._targetForEdition().find('.oe_structure.oe_empty, [data-oe-type="html"]');
        this.$editorMessageElements = $editable
            .not('[data-editor-message]')
            .attr('data-editor-message', _t('DRAG BUILDING BLOCKS HERE'));
        $editable.filter(':empty').attr('contenteditable', false);
    },
    /**
     * Returns the target for edition.
     *
     * @private
     * @returns {JQuery}
     */
    _targetForEdition: function () {
        return $('#wrapwrap'); // TODO should know about this element another way
    },
    /**
     * Reloads the page in non-editable mode, with the right scrolling.
     *
     * @private
     * @returns {Deferred} (never resolved, the page is reloading anyway)
     */
    _reload: function () {
        $('body').addClass('o_wait_reload');
        this.wysiwyg.destroy();
        this.$el.hide();
        window.location.hash = 'scrollTop=' + window.document.body.scrollTop;
        window.location.reload(true);
        return new Promise(function () {});
    },
    /**
     * @private
     */
    _wysiwygInstance: function () {
        // todo: retrieve other config if there is no #wrap element on the page (eg. product, blog, ect.)
        let collaborationConfig = {};
        // todo: To uncomment when enabling the collaboration on website.
        // const $wrap = $('#wrapwrap #wrap[data-oe-model][data-oe-field][data-oe-id]');
        // if ($wrap.length) {
        //     collaborationConfig = {
        //         collaborationChannel: {
        //             collaborationModelName: $wrap.attr('data-oe-model'),
        //             collaborationFieldName: $wrap.attr('data-oe-field'),
        //             collaborationResId: parseInt($wrap.attr('data-oe-id')),
        //         }
        //     };
        // }

        var context;
        this.trigger_up('context_get', {
            callback: function (ctx) {
                context = ctx;
            },
        });
        const params = Object.assign({
            snippets: 'website.snippets',
            recordInfo: {
                context: context,
                data_res_model: 'website',
                data_res_id: context.website_id,
            },
            enableWebsite: true,
            discardButton: true,
            saveButton: true,
            devicePreview: true,
            savableSelector: this.savableSelector,
            isRootEditable: false,
            controlHistoryFromDocument: true,
            getContentEditableAreas: this._getContentEditableAreas.bind(this),
        }, collaborationConfig);
        return wysiwygLoader.createWysiwyg(this,
            Object.assign(params, this.wysiwygOptions),
            ['website.compiled_assets_wysiwyg']
        );
    },


    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Called when content will be destroyed in the page. Notifies the
     * WebsiteRoot that is should stop the public widgets.
     *
     * @private
     * @param {GigaEvent} ev
     */
    _onContentWillBeDestroyed: function (ev) {
        this.trigger_up('widgets_stop_request', {
            $target: ev.data.$target,
        });
    },
    /**
     * Called when content was recreated in the page. Notifies the
     * WebsiteRoot that is should start the public widgets.
     *
     * @private
     * @param {GigaEvent} ev
     */
    _onContentWasRecreated: function (ev) {
        this.trigger_up('widgets_start_request', {
            editableMode: true,
            $target: ev.data.$target,
        });
    },
    /**
     * Called when edition will stop. Notifies the
     * WebsiteRoot that is should stop the public widgets.
     *
     * @private
     * @param {GigaEvent} ev
     */
    _onEditionWillStop: function (ev) {
        this.$editorMessageElements && this.$editorMessageElements.removeAttr('data-editor-message');
        this.trigger_up('widgets_stop_request', {
            $target: this._targetForEdition(),
        });
        this.observer.disconnect();
    },
    /**
     * Called when edition was stopped. Notifies the
     * WebsiteRoot that is should start the public widgets.
     *
     * @private
     * @param {GigaEvent} ev
     */
    _onEditionWasStopped: function (ev) {
        this.editModeEnable = false;
    },
    /**
     * Called when a snippet is about to be cloned in the page. Notifies the
     * WebsiteRoot that is should destroy the animations for this snippet.
     *
     * @private
     * @param {GigaEvent} ev
     */
    _onSnippetWillBeCloned: function (ev) {
        this.trigger_up('widgets_stop_request', {
            $target: ev.data.$target,
        });
    },
    /**
     * Called when a snippet is cloned in the page. Notifies the WebsiteRoot
     * that is should start the public widgets for this snippet and the snippet it
     * was cloned from.
     *
     * @private
     * @param {GigaEvent} ev
     */
    _onSnippetCloned: function (ev) {
        this.trigger_up('widgets_start_request', {
            editableMode: true,
            $target: ev.data.$target,
        });
        // TODO: remove in saas-12.5, undefined $origin will restart #wrapwrap
        if (ev.data.$origin) {
            this.trigger_up('widgets_start_request', {
                editableMode: true,
                $target: ev.data.$origin,
            });
        }
    },
    /**
     * Called when a snippet is dropped in the page. Notifies the WebsiteRoot
     * that is should start the public widgets for this snippet. Also marks the
     * wrapper element as non-empty and makes it editable.
     *
     * @private
     * @param {GigaEvent} ev
     */
    _onSnippetDropped: function (ev) {
        this._targetForEdition().find('.oe_structure.oe_empty, [data-oe-type="html"]')
            .attr('contenteditable', true);
        ev.data.addPostDropAsync(new Promise(resolve => {
            this.trigger_up('widgets_start_request', {
                editableMode: true,
                $target: ev.data.$target,
                onSuccess: () => resolve(),
            });
        }));
    },
    /**
     * Called when a snippet is removed from the page. If the wrapper element is
     * empty, marks it as such and shows the editor messages.
     *
     * @private
     * @param {GigaEvent} ev
     */
    _onSnippetRemoved: function (ev) {
        const $editable = this._targetForEdition().find('.oe_structure.oe_empty, [data-oe-type="html"]');
        if (!$editable.children().length) {
            $editable.empty(); // remove any superfluous whitespace
            this._addEditorMessages();
        }
    },
    /**
     * Snippet (menu_data) can request to save the document to leave the page
     *
     * @private
     * @param {GigaEvent} ev
     * @param {object} ev.data
     * @param {function} ev.data.onSuccess
     * @param {function} ev.data.onFailure
     */
    _onSnippetRequestSave: function (ev) {
        ev.stopPropagation();
        const restore = dom.addButtonLoadingEffect($('button[data-action=save]')[0]);
        this.save(ev.data.reload).then(ev.data.onSuccess, ev.data.onFailure).then(restore).guardedCatch(restore);
    },
    /**
     * Asks the user if they really wants to discard their changes (if any),
     * then simply reloads the page if they want to.
     *
     * @private
     * @param {GigaEvent} ev
     */
    _onSnippetRequestCancel: function (ev) {
        ev.stopPropagation();
        this.cancel();
    },
});

registry.category("website_navbar_widgets").add("EditPageMenu", {
    Widget: EditPageMenu,
    selector: '#edit-page-menu',
});

return EditPageMenu;
});
