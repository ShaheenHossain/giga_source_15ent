/** @giga-module */

import { useService } from "@web/core/utils/hooks";
import { sprintf } from "@web/core/utils/strings";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class NewViewDialog extends ConfirmationDialog {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.studio = useService("studio");
        this.user = useService("user");
        this.mandatoryStopDate = ["gantt", "cohort"].includes(this.viewType);

        this.title = sprintf(this.env._t("Generate %s View"), this.viewType);

        this.fieldsChoice = {
            date_start: null,
            date_stop: null,
        };
    }

    get viewType() {
        return this.props.viewType;
    }

    async willStart() {
        const fieldsGet = await this.orm.call(this.studio.editedAction.res_model, "fields_get");
        const fields = Object.entries(fieldsGet).map(([fName, field]) => {
            field.name = fName;
            return field;
        });
        fields.sort((first, second) => {
            if (first.string === second.string) {
                return 0;
            }
            if (first.string < second.string) {
                return -1;
            }
            if (first.string > second.string) {
                return 1;
            }
        });
        this.computeSpecificFields(fields);
        return super.willStart();
    }

    /**
     * Compute date, row and measure fields.
     */
    computeSpecificFields(fields) {
        this.dateFields = [];
        this.rowFields = [];
        this.measureFields = [];
        fields.forEach((field) => {
            if (field.store) {
                // date fields
                if (field.type === "date" || field.type === "datetime") {
                    this.dateFields.push(field);
                }
                // row fields
                if (this.constructor.GROUPABLE_TYPES.includes(field.type)) {
                    this.rowFields.push(field);
                }
                // measure fields
                if (this.constructor.MEASURABLE_TYPES.includes(field.type)) {
                    // id and sequence are not measurable
                    if (field.name !== "id" && field.name !== "sequence") {
                        this.measureFields.push(field);
                    }
                }
            }
        });
        if (this.dateFields.length) {
            this.fieldsChoice.date_start = this.dateFields[0].name;
            this.fieldsChoice.date_stop = this.dateFields[0].name;
        }
    }

    async _confirm() {
        await this.rpc("/web_studio/create_default_view", {
            model: this.studio.editedAction.res_model,
            view_type: this.viewType,
            attrs: this.fieldsChoice,
            context: this.user.context,
        });
        super._confirm();
    }
}
NewViewDialog.bodyTemplate = "web_studio.NewViewFieldsSelector";
NewViewDialog.footerTemplate = "web_studio.OwlNewViewDialogFooter";
NewViewDialog.GROUPABLE_TYPES = ["many2one", "char", "boolean", "selection", "date", "datetime"];
NewViewDialog.MEASURABLE_TYPES = ["integer", "float"];
NewViewDialog.size = "modal-md";
NewViewDialog.props = Object.assign(Object.create(ConfirmationDialog.props), {
    viewType: String,
    title: { type: String, optional: true },
    body: { type: String, optional: true },
});
