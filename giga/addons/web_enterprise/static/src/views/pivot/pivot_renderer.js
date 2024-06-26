/** @giga-module */

import { patch } from "@web/core/utils/patch";
import { PivotRenderer } from "@web/views/pivot/pivot_renderer";
import { useEffect } from "@web/core/utils/hooks";

patch(PivotRenderer.prototype, "web_enterprise.PivotRendererMobile", {
    setup() {
        this._super();
        if (this.env.isSmall) {
            useEffect(() => {
                const tooltipElems = this.el.querySelectorAll("*[data-tooltip]");
                for (const el of tooltipElems) {
                    el.removeAttribute("data-tooltip");
                    el.removeAttribute("data-tooltip-position");
                }
            });
        }
    },

    getPadding(cell) {
        if (this.env.isSmall) {
            return 5 + cell.indent * 5;
        }
        return this._super(...arguments);
    },
});
