/** @giga-module **/

import { StudioActionContainer } from "../studio_action_container";
import { actionService } from "@web/webclient/actions/action_service";
import { useBus, useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

import { EditorMenu } from "./editor_menu/editor_menu";

import { mapDoActionOptionAPI } from "@web/legacy/backend_utils";

const { Component, core, hooks } = owl;

const editorTabRegistry = registry.category("web_studio.editor_tabs");

const actionServiceStudio = {
    dependencies: ["studio"],
    start(env) {
        const action = actionService.start(env);
        const _doAction = action.doAction;

        async function doAction(actionRequest, options) {
            if (actionRequest === "web_studio.action_edit_report") {
                return env.services.studio.setParams({
                    editedReport: options.report,
                });
            }
            return _doAction(...arguments);
        }

        return Object.assign(action, { doAction });
    },
};

export class Editor extends Component {
    setup() {
        this.studio = useService("studio");

        hooks.useSubEnv({
            bus: new core.EventBus(),
        });
        this.env.services = Object.assign({}, this.env.services);
        this.env.services.router = {
            current: { hash: {} },
            pushState() {},
        };
        // Assuming synchronousness
        this.env.services.action = actionServiceStudio.start(this.env);
        this.actionService = useService("action");

        useBus(this.studio.bus, "UPDATE", async () => {
            const action = await this.getStudioAction();
            this.actionService.doAction(action, {
                clearBreadcrumbs: true,
            });
        });
    }

    async willStart() {
        this.initialAction = await this.getStudioAction();
    }

    switchView(ev) {
        const { viewType } = ev.detail;
        this.studio.setParams({ viewType, editorTab: "views" });
    }
    switchViewLegacy(ev) {
        this.studio.setParams({ viewType: ev.detail.view_type });
    }

    onSwitchTab(ev) {
        this.studio.setParams({ editorTab: ev.detail.tab });
    }

    async getStudioAction() {
        const { editorTab, editedAction, editedReport } = this.studio;
        const tab = editorTabRegistry.get(editorTab);
        if (tab.action) {
            return tab.action;
        } else if (editorTab === "reports" && editedReport) {
            return "web_studio.report_editor";
        } else {
            return this.rpc("/web_studio/get_studio_action", {
                action_name: editorTab,
                model: editedAction.res_model,
                view_id: editedAction.view_id && editedAction.view_id[0], // Not sure it is correct or desirable
            });
        }
    }

    onDoAction(ev) {
        // @legacy;
        const payload = ev.detail;
        const legacyOptions = mapDoActionOptionAPI(payload.options);
        this.actionService.doAction(
            payload.action,
            Object.assign(legacyOptions || {}, { clearBreadcrumbs: true })
        );
    }
}
Editor.template = "web_studio.Editor";
Editor.components = {
    EditorMenu,
    StudioActionContainer,
};
