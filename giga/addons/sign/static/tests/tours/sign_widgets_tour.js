giga.define('sign_widgets_tour', function (require) {
    "use strict";

    var core = require('web.core');
    var tour = require('web_tour.tour');

    var _t = core._t;

    tour.register('sign_widgets_tour', {
        test: true,
        url: "/web",
        },
         [tour.stepUtils.showAppsMenuItem(),
            {
                content: "Settings",
                trigger: 'a[data-menu-xmlid="base.menu_administration"]',
                run: 'click',
            },
            {
                content: "Users",
                trigger: 'div#invite_users button.o_web_settings_access_rights',
                run: 'click',
            },
            {
                content: "Mitchel",
                trigger: 'table.o_list_table td.o_data_cell:contains(Admin)',
                run: 'click',
            },

            {
                content: "Preference tab",
                trigger: 'a.nav-link:contains("' + _t("Preferences") + '")',
                run: 'click',
            },
            {
                content: "Edit Mitchell",
                trigger: 'div.o_cp_buttons .o_form_button_edit',
                extra_trigger: '.o_signature', // Check widget sign is present
                run: 'click',
            },
            {
                content: "Editor loaded",
                trigger: '.note-editable',
            },
            {
                content: "Click on widget sign",
                trigger: '.o_signature:first',
                run: 'click',
            },
            {
                content: "Click on auto button",
                trigger: '.o_web_sign_auto_button',
                run: 'click',
            },
            {
                content: "Click on style button",
                trigger: 'div.o_web_sign_auto_select_style > a',
                run: 'click',
            },
            {
                content: "Select a style",
                trigger: 'div.o_web_sign_auto_font_list > a:nth-child(3)',
                run: 'click',
            },
            {
                content: "Click on style button",
                trigger: 'div.o_web_sign_auto_select_style > a',
                run: 'click',
            },
            {
                content: "Select a style",
                trigger: 'div.o_web_sign_auto_font_list > a:nth-child(2)',
                run: 'click',
            },
            {
                content: "Sign",
                trigger: 'button.btn-primary:contains("Adopt and Sign")',
                run: 'click',
                extra_trigger: 'canvas.jSignature',
                run: function () {
                    setTimeout(() => {
                        this.$anchor.click();
                    }, 1000);
                },
            },
            {
                content: "Save Mitchell",
                trigger: 'button.o_form_button_save',
                run: 'click',
            },
        ]
    );
});
