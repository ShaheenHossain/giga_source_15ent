/** @giga-module **/

import BarcodePickingModel from '@stock_barcode/models/barcode_picking_model';
import {_t} from "web.core";

export default class BarcodePickingBatchModel extends BarcodePickingModel {
    constructor(params) {
        super(...arguments);
        this.formViewReference = 'stock_barcode_picking_batch.stock_barcode_batch_picking_view_info';
        this.lineFormViewReference = 'stock_barcode_picking_batch.stock_move_line_product_selector_inherit';
        this.validateMessage = _t("The Batch Transfer has been validated");
        this.validateMethod = 'action_done';
    }

    setData(data) {
        super.setData(...arguments);
        // In case it's a new batch, we must display the pickings selector first.
        if (this.record.state === 'draft' && this.record.picking_ids.length === 0) {
            this.selectedPickings = [];
            this._allowedPickings = data.data.allowed_pickings;
            this.pickingTypes = data.data.picking_types;
            for (const picking of this._allowedPickings) {
                if (picking.user_id) {
                    picking.user_id = this.cache.getRecord('res.users', picking.user_id);
                }
            }
            if (!this.record.picking_type_code) {
                this.selectedPickingTypeId = false;
            }
        }
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    get allowedPickings() {
        const pickingTypeId = this.record.picking_type_id;
        if (!pickingTypeId || !this._allowedPickings) {
            return [];
        }
        return this._allowedPickings.filter(picking => picking.picking_type_id === pickingTypeId);
    }

    get barcodeInfo() {
        if ((this.needPickings || this.needPickingType) && !this._allowedPickings.length) {
            // Special case: the batch need to be configured but there is no pickings available.
            return {
                class: 'picking_batch_not_possible',
                message: _t("No ready transfers found"),
                warning: true,
            };
        } else if (this.needPickingType) {
            return {
                class: 'picking_batch_select_type',
                message: _t("Select an operation type for batch transfer"),
            };
        } else if (this.needPickings) {
            return {
                class: 'picking_batch_select_transfers',
                message: _t("Select transfers for batch transfer"),
            };
        } else if (this.isDone) {
            return {
                class: 'picking_already_done',
                message: _t("This batch transfer is already done"),
                warning: true,
            };
        } else if (this.isCancelled) {
            return {
                class: 'picking_already_cancelled',
                message: _t("This batch transfer is cancelled"),
                warning: true,
            };
        } else if (this.record.state === 'draft') {
            return {
                class: 'picking_batch_draft',
                message:  _t("This batch transfer is still draft, it must be confirmed before being processed"),
                warning: true,
            };
        }
        return super.barcodeInfo;
    }

    get canBeProcessed() {
        if (this.record.state === 'draft') {
            return this.needPickingType || this.needPickings;
        }
        return super.canBeProcessed;
    }

    get canConfirmSelection() {
        if (this.needPickingType) {
            return Boolean(this.selectedPickingTypeId);
        } else if (this.needPickings) {
            return Boolean(this.selectedPickings.length);
        }
    }

    /**
     * Depending of the batch's state, will confirm the picking type selection or the pickings
     * selection. In the latter, it will confirm the batch transfer and reload its data.
     */
    async confirmSelection() {
        if (this.needPickingType && this.selectedPickingTypeId) {
            // Applies the selected picking type to the batch.
            this.record.picking_type_id = this.selectedPickingTypeId;
            this.trigger('update');
        } else if (this.needPickings && this.selectedPickings.length) {
            // Adds the selected pickings to the batch.
            const data = await this.orm.call(
                'stock.picking.batch',
                'action_add_pickings_and_confirm',
                [[this.params.id],
                {
                    picking_type_id: this.record.picking_type_id,
                    picking_ids: this.selectedPickings,
                    state: 'in_progress',
                }]
            );
            await this.refreshCache(data.records);
            this.displayBarcodeLines();
        }
    }

    groupKey(line) {
        return `${line.picking_id.id}_${line.product_id.id}`;
    }

    get needPickings() {
        return this.record.state === 'draft' && this.record.picking_ids.length === 0;
    }

    get needPickingType() {
        return this.record.state === 'draft' && !this.record.picking_type_id;
    }

    get printButtons() {
        return [{
            name: _t("Print Batch Transfer"),
            class: 'o_print_picking_batch',
            method: 'action_print',
        }];
    }

    selectOption(id) {
        if (this.needPickingType) { // Selects a picking type.
            this.selectedPickingTypeId = this.selectedPickingTypeId === id ? false : id;
            this.trigger('update');
        } else if (this.needPickings) { // Selects a picking.
            if (this.selectedPickings.indexOf(id) !== -1) {
                // If picking already selected, removes it from the selected ones.
                this.selectedPickings.splice(this.selectedPickings.indexOf(id), 1);
            } else {
                this.selectedPickings.push(id);
            }
            this.trigger('update');
        }
    }

    get useExistingLots() {
        return this.picking.use_existing_lots;
    }

    // -------------------------------------------------------------------------
    // Private
    // -------------------------------------------------------------------------

    _cancelNotification() {
        this.trigger('notification', {
            message: _t("The batch picking has been cancelled"),
        });
    }

    _canOverrideTrackingNumber(line) {
        return this.getQtyDone(line) === 0;
    }

    _createLinesState() {
        const lines = super._createLinesState();
        const pickings = this.record.picking_ids;
        const suggestedPackagesByPicking = {};
        this.colorByPickingId = new Map(pickings.map((p, i) => [p, i * (360 / pickings.length)]));

        for (const line of lines) {
            line.colorLine = this.colorByPickingId.get(line.picking_id);
            line.picking_id = line.picking_id && this.cache.getRecord('stock.picking', line.picking_id);
            // Checks if a line has a result package, and if so, links it to the according picking.
            if (line.result_package_id && !suggestedPackagesByPicking[line.picking_id.id]) {
                suggestedPackagesByPicking[line.picking_id.id] = line.result_package_id.name;
            }
        }
        // Suggests a package to scan for each picking's line if its picking is linked to a package.
        for (const line of lines) {
            if (!line.result_package_id && suggestedPackagesByPicking[line.picking_id.id]) {
                line.suggested_package = suggestedPackagesByPicking[line.picking_id.id];
            }
        }
        return lines;
    }

    _createState() {
        super._createState(...arguments);
        if (this.record.picking_ids.length < 1) {
            return new Error("No picking related");
        }
        // Get the first picking as a reference for some fields the batch hasn't.
        this.picking = this.cache.getRecord('stock.picking', this.record.picking_ids[0]);
    }

    _defaultLocationId() {
        return this.picking && this.picking.location_id;
    }

    _defaultDestLocationId() {
        return this.picking && this.picking.location_dest_id;
    }

    _getNewLineDefaultValues() {
        // Adds the default picking id and its corresponding color on the line.
        const defaultValues = super._getNewLineDefaultValues();
        let line = this.selectedLine;
        if (!line) {
            if (this.lastScannedPackage) {
                const lines = this._moveEntirePackage() ? this.packageLines : this.pageLines;
                line = lines.find(l => l.package_id && l.package_id.id === this.lastScannedPackage);
            } else if (this.pageLines.length) {
                line = this.pageLines[0];
            }
        }
        // Get the line's picking as the default one, or take the batch's first one.
        const defaultPicking = (line && line.picking_id) || this.picking;
        defaultValues.colorLine = this.colorByPickingId.get(defaultPicking.id);
        defaultValues.picking_id = defaultPicking;
        return defaultValues;
    }

    _getNewLineDefaultContext() {
        const defaultContextValues = super._getNewLineDefaultContext();
        const batch = this.cache.getRecord(this.params.model, this.params.id);
        defaultContextValues.default_picking_id = batch.picking_ids[0];
        return defaultContextValues;
    }

    _incrementTrackedLine() {
        return !(this.picking.use_create_lots || this.picking.use_existing_lots);
    }

    _moveEntirePackage() {
        return this.picking.picking_type_entire_packs;
    }
}
