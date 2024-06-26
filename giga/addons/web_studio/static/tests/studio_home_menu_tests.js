/** @giga-module **/

import { StudioHomeMenu } from "@web_studio/client_action/studio_home_menu/studio_home_menu";
import { MODES } from "@web_studio/studio_service";

import { makeFakeEnterpriseService } from "@web_enterprise/../tests/mocks";
import { makeFakeNotificationService } from "@web/../tests/helpers/mock_services";
import { userService } from "@web/core/user_service";
import { uiService } from "@web/core/ui/ui_service";
import { hotkeyService } from "@web/core/hotkeys/hotkey_service";

import { getFixture } from "@web/../tests/helpers/utils";
import { makeTestEnv } from "@web/../tests/helpers/mock_env";
import { registry } from "@web/core/registry";

import testUtils from "web.test_utils";

import { dialogService } from "@web/core/dialog/dialog_service";
import { makeFakeRPCService } from "@web/../tests/helpers/mock_services";

const { Component, core, hooks, mount, tags } = owl;
const { EventBus } = core;
const serviceRegistry = registry.category("services");

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

async function createStudioHomeMenu(homeMenuProps) {
    class Parent extends Component {
        constructor() {
            super(...arguments);
            this.homeMenuRef = hooks.useRef("home-menu");
            this.homeMenuProps = homeMenuProps;
        }
        get DialogContainer() {
            return registry.category("main_components").get("DialogContainer");
        }
    }
    Parent.components = { StudioHomeMenu };
    Parent.template = tags.xml`
        <div>
            <StudioHomeMenu t-ref="home-menu" t-props="homeMenuProps"/>
            <div class="o_dialog_container"/>
            <t t-component="DialogContainer.Component" t-props="DialogContainer.props"/>
        </div>`;
    const env = await makeTestEnv();
    const target = getFixture();
    const parent = await mount(Parent, { env, target });
    return {
        studioHomeMenu: parent.homeMenuRef.comp,
        destroy: parent.destroy.bind(parent),
    };
}

// -----------------------------------------------------------------------------
// Tests
// -----------------------------------------------------------------------------

let homeMenuProps;
let bus;

QUnit.module("Studio", (hooks) => {
    hooks.beforeEach(() => {
        bus = new EventBus();

        const fakeEnterpriseService = makeFakeEnterpriseService();
        const fakeNotificationService = makeFakeNotificationService();
        const fakeHomeMenuService = {
            start() {
                return {
                    toggle() {},
                };
            },
        };
        const fakeMenuService = {
            start() {
                return {
                    setCurrentMenu(menu) {
                        bus.trigger("menu:setCurrentMenu", menu.id);
                    },
                    reload() {
                        bus.trigger("menu:reload");
                    },
                    getMenu() {
                        return {};
                    },
                };
            },
        };
        const fakeStudioService = {
            start() {
                return {
                    MODES,
                    open() {
                        bus.trigger("studio:open", ...arguments);
                    },
                };
            },
        };
        const fakeHTTPService = {
            start() {
                return {};
            },
        };

        serviceRegistry.add("enterprise", fakeEnterpriseService);
        serviceRegistry.add("home_menu", fakeHomeMenuService);
        serviceRegistry.add("http", fakeHTTPService);
        serviceRegistry.add("menu", fakeMenuService);
        serviceRegistry.add("notification", fakeNotificationService);
        serviceRegistry.add("user", userService);
        serviceRegistry.add("studio", fakeStudioService);
        serviceRegistry.add("hotkey", hotkeyService);
        serviceRegistry.add("dialog", dialogService);
        serviceRegistry.add("ui", uiService);

        homeMenuProps = {
            apps: [
                {
                    actionID: 121,
                    id: 1,
                    appID: 1,
                    label: "Discuss",
                    parents: "",
                    webIcon: "mail,static/description/icon.png",
                    webIconData: "/web_enterprise/static/img/default_icon_app.png",
                    xmlid: "app.1",
                },
                {
                    actionID: 122,
                    id: 2,
                    appID: 2,
                    label: "Calendar",
                    parents: "",
                    webIcon: {
                        backgroundColor: "#C6572A",
                        color: "#FFFFFF",
                        iconClass: "fa fa-diamond",
                    },
                    xmlid: "app.2",
                },
                {
                    actionID: 123,
                    id: 3,
                    appID: 3,
                    label: "Contacts",
                    parents: "",
                    webIcon: false,
                    webIconData: "/web_enterprise/static/img/default_icon_app.png",
                    xmlid: "app.3",
                },
            ],
        };
    });

    QUnit.module("StudioHomeMenu");

    QUnit.test("simple rendering", async function (assert) {
        assert.expect(21);

        const { studioHomeMenu, destroy } = await createStudioHomeMenu(homeMenuProps);

        // Main div
        assert.hasClass(studioHomeMenu.el, "o_home_menu");

        // Hidden elements
        assert.isNotVisible(
            studioHomeMenu.el.querySelector(".database_expiration_panel"),
            "Expiration panel should not be visible"
        );
        assert.hasClass(studioHomeMenu.el, "o_search_hidden");

        // App list
        assert.containsOnce(studioHomeMenu.el, "div.o_apps");
        assert.containsN(
            studioHomeMenu.el,
            "div.o_apps > a.o_app.o_menuitem",
            4,
            "should contain 3 normal app icons + the new app button"
        );

        // App with image
        const firstApp = studioHomeMenu.el.querySelector("div.o_apps > a.o_app.o_menuitem");
        assert.strictEqual(firstApp.dataset.menuXmlid, "app.1");
        assert.containsOnce(firstApp, "div.o_app_icon");
        assert.strictEqual(
            firstApp.querySelector("div.o_app_icon").style.backgroundImage,
            'url("/web_enterprise/static/img/default_icon_app.png")'
        );
        assert.containsOnce(firstApp, "div.o_caption");
        assert.strictEqual(firstApp.querySelector("div.o_caption").innerText, "Discuss");
        assert.containsOnce(firstApp, ".o_web_studio_edit_icon i");

        // App with custom icon
        const secondApp = studioHomeMenu.el.querySelectorAll("div.o_apps > a.o_app.o_menuitem")[1];
        assert.strictEqual(secondApp.dataset.menuXmlid, "app.2");
        assert.containsOnce(secondApp, "div.o_app_icon");
        assert.strictEqual(
            secondApp.querySelector("div.o_app_icon").style.backgroundColor,
            "rgb(198, 87, 42)",
            "Icon background color should be #C6572A"
        );
        assert.containsOnce(secondApp, "i.fa.fa-diamond");
        assert.strictEqual(
            secondApp.querySelector("i.fa.fa-diamond").style.color,
            "rgb(255, 255, 255)",
            "Icon color should be #FFFFFF"
        );
        assert.containsOnce(secondApp, ".o_web_studio_edit_icon i");

        // New app button
        assert.containsOnce(
            studioHomeMenu.el,
            "div.o_apps > a.o_app.o_web_studio_new_app",
            'should contain a "New App icon"'
        );
        const newApp = studioHomeMenu.el.querySelector("a.o_app.o_web_studio_new_app");
        assert.strictEqual(
            newApp.querySelector("div.o_app_icon").style.backgroundImage,
            'url("/web_studio/static/src/img/default_icon_app.png")',
            "Image source URL should end with '/web_studio/static/src/img/default_icon_app.png'"
        );
        assert.containsOnce(newApp, "div.o_caption");
        assert.strictEqual(newApp.querySelector("div.o_caption").innerText, "New App");

        destroy();
    });

    QUnit.test("Click on a normal App", async function (assert) {
        assert.expect(3);

        bus.on("studio:open", null, (mode, actionId) => {
            assert.strictEqual(mode, MODES.EDITOR);
            assert.strictEqual(actionId, 121);
        });
        bus.on("menu:setCurrentMenu", null, (menuId) => {
            assert.strictEqual(menuId, 1);
        });
        const { studioHomeMenu, destroy } = await createStudioHomeMenu(homeMenuProps);

        await testUtils.dom.click(studioHomeMenu.el.querySelector(".o_menuitem"));

        destroy();
    });

    QUnit.test("Click on new App", async function (assert) {
        assert.expect(1);

        bus.on("studio:open", null, (mode) => {
            assert.strictEqual(mode, MODES.APP_CREATOR);
        });
        bus.on("menu:setCurrentMenu", null, () => {
            throw new Error("should not update the current menu");
        });
        const { studioHomeMenu, destroy } = await createStudioHomeMenu(homeMenuProps);

        await testUtils.dom.click(studioHomeMenu.el.querySelector("a.o_app.o_web_studio_new_app"));

        destroy();
    });

    QUnit.test("Click on edit icon button", async function (assert) {
        assert.expect(11);

        const { studioHomeMenu, destroy } = await createStudioHomeMenu(homeMenuProps);

        // TODO: we should maybe check icon visibility comes on mouse over
        const firstEditIconButton = studioHomeMenu.el.querySelector(".o_web_studio_edit_icon i");
        await testUtils.dom.click(firstEditIconButton);

        const dialog = document.querySelector("div.modal");
        assert.containsOnce(dialog, "header.modal-header");
        assert.strictEqual(
            dialog.querySelector("header.modal-header h4").innerText,
            "Edit Application Icon"
        );

        assert.containsOnce(
            dialog,
            ".modal-content.o_web_studio_edit_menu_icon_modal .o_web_studio_icon_creator"
        );

        assert.containsOnce(dialog, "footer.modal-footer");
        assert.containsN(dialog, "footer button", 2);

        const buttons = dialog.querySelectorAll("footer button");
        const firstButton = buttons[0];
        const secondButton = buttons[1];

        assert.strictEqual(firstButton.innerText, "CONFIRM");
        assert.hasClass(firstButton, "btn-primary");

        assert.strictEqual(secondButton.innerText, "CANCEL");
        assert.hasClass(secondButton, "btn-secondary");

        await testUtils.dom.click(secondButton);

        assert.strictEqual(document.querySelector("div.modal"), null);

        await testUtils.dom.click(firstEditIconButton);
        await testUtils.dom.click(document.querySelector("footer button"));

        assert.strictEqual(document.querySelector("div.modal"), null);

        destroy();
    });

    QUnit.test("edit an icon", async function (assert) {
        assert.expect(3);

        const mockRPC = (route, args) => {
            if (route === "/web_studio/edit_menu_icon") {
                assert.deepEqual(args, {
                    context: {
                        lang: "en",
                        tz: "taht",
                        uid: 7,
                    },
                    icon: ["fa fa-balance-scale", "#f1c40f", "#34495e"],
                    menu_id: 1,
                });
            }
        };
        registry.category("services").add("rpc", makeFakeRPCService(mockRPC), { force: true });

        const { studioHomeMenu, destroy } = await createStudioHomeMenu(homeMenuProps);

        await testUtils.dom.click(studioHomeMenu.el.querySelector(".o_web_studio_edit_icon i"));
        const dialog = document.querySelector("div.modal");
        await testUtils.dom.click(dialog.querySelector(".o_web_studio_upload a"));

        assert.doesNotHaveClass(
            dialog.querySelector(".o_web_studio_icon .o_app_icon i"),
            "fa-balance-scale"
        );

        // Change the icon's pictogram
        await testUtils.dom.click(dialog.querySelectorAll(".o_web_studio_selector")[2]);
        await testUtils.dom.click(
            dialog.querySelector(".o_web_studio_selector .fa.fa-balance-scale")
        );

        assert.hasClass(
            dialog.querySelector(".o_web_studio_icon .o_app_icon i"),
            "fa-balance-scale"
        );

        await testUtils.dom.click(dialog.querySelector("footer button")); // trigger save
        destroy();
    });
});
