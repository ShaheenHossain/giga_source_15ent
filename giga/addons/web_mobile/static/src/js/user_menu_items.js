/** @giga-module **/

import mobile from "web_mobile.core";

export function shortcutItem(env) {
    return {
        type: "item",
        id: "web_mobile.shortcut",
        description: env._t("Add to Home Screen"),
        callback: () => {
            const { hash } = env.services.router.current;
            if (hash.menu_id) {
                const menu = env.services.menu.getMenu(hash.menu_id);
                mobile.methods.addHomeShortcut({
                    title: document.title,
                    shortcut_url: document.URL,
                    web_icon: menu && menu.webIconData,
                });
            } else {
                env.services.notification.notify({
                    message: env._t("No shortcut for Home Menu"),
                });
            }
        },
        sequence: 100,
    };
}

export function switchAccountItem(env) {
    return {
        type: "item",
        id: "web_mobile.switch",
        description: env._t("Switch/Add Account"),
        callback: () => {
            mobile.methods.switchAccount();
        },
        sequence: 100,
    };
}
