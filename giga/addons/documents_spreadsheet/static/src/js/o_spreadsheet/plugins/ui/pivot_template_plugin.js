giga.define("documents_spreadsheet.PivotTemplatePlugin", function (require) {
    "use strict";

    const spreadsheet = require("documents_spreadsheet.spreadsheet");
    const CommandResult = require("documents_spreadsheet.CommandResult");
    const { pivotFormulaRegex } = require("documents_spreadsheet.pivot_utils");
    const { parse, astToFormula } = spreadsheet;

    class PivotTemplatePlugin extends spreadsheet.UIPlugin {
        constructor(getters, history, dispatch, config) {
            super(getters, history, dispatch, config);
            this.rpc = config.evalContext.env ? config.evalContext.env.services.rpc : undefined;
        }

        allowDispatch(cmd) {
            switch (cmd.type) {
                case "CONVERT_PIVOT_TO_TEMPLATE":
                case "CONVERT_PIVOT_FROM_TEMPLATE": {
                    const caches = this.getters
                        .getPivotIds()
                        .map(this.getters.getPivotStructureData);
                    if (caches.includes(undefined)) {
                        return CommandResult.PivotCacheNotLoaded;
                    }
                    break;
                }
            }
            return CommandResult.Success;
        }

        /**
         * Handle a spreadsheet command
         *
         * @param {Object} cmd Command
         */
        handle(cmd) {
            switch (cmd.type) {
                case "CONVERT_PIVOT_TO_TEMPLATE":
                    this._convertFormulas(
                        this._getCells(pivotFormulaRegex),
                        this._absoluteToRelative.bind(this),
                        this.getters.getPivotIds().map(this.getters.getPivotForRPC)
                    );
                    break;
                case "CONVERT_PIVOT_FROM_TEMPLATE":
                    this._convertFormulas(
                        this._getCells(pivotFormulaRegex),
                        this._relativeToAbsolute.bind(this),
                        this.getters.getPivotIds().map(this.getters.getPivotForRPC)
                    );
                    this._removeInvalidPivotRows();
                    break;
            }
        }

        /**
         * Applies a transformation function to all given formula cells.
         * The transformation function takes as fist parameter the cell AST and should
         * return a modified AST.
         * Any additional parameter is forwarded to the transformation function.
         *
         * @param {Array<Object>} cells
         * @param {Function} convertFunction
         * @param {...any} args
         */
        _convertFormulas(cells, convertFunction, ...args) {
            cells.forEach((cell) => {
                if (cell.isFormula()) {
                    const { col, row, sheetId } = this.getters.getCellPosition(cell.id);
                    const ast = convertFunction(parse(cell.normalizedText), ...args);
                    if (ast) {
                        const content = this.getters.buildFormulaContent(
                            sheetId,
                            `=${astToFormula(ast)}`,
                            cell.dependencies
                        );
                        this.dispatch("UPDATE_CELL", {
                            content,
                            sheetId,
                            col,
                            row,
                        });
                    } else {
                        this.dispatch("CLEAR_CELL", {
                            sheetId,
                            col,
                            row,
                        });
                    }
                }
            });
        }

        /**
         * Return all formula cells matching a given regular expression.
         *
         * @param {RegExp} regex
         * @returns {Array<Object>}
         */
        _getCells(regex) {
            return this.getters
                .getSheets()
                .map((sheet) =>
                    Object.values(this.getters.getCells(sheet.id)).filter(
                        (cell) =>
                            cell.isFormula() &&
                            regex.test(this.getters.getFormulaCellContent(sheet.id, cell))
                    )
                )
                .flat();
        }

        /**
         * return AST from an relative PIVOT ast to a absolute PIVOT ast (sheet -> template)
         * *
         * relative PIVOTS formulas use the position while Absolute PIVOT
         * formulas use hardcoded ids
         *
         * e.g.
         * The following relative formula
         *      `PIVOT("1","probability","product_id",PIVOT.POSITION("1","product_id",0),"bar","110")`
         * is converted to
         *      `PIVOT("1","probability","product_id","37","bar","110")`
         *
         * @param {Object} ast
         * @returns {Object}
         */
        _relativeToAbsolute(ast) {
            switch (ast.type) {
                case "FUNCALL":
                    switch (ast.value) {
                        case "PIVOT.POSITION":
                            return this._pivotPositionToAbsolute(ast);
                        default:
                            return Object.assign({}, ast, {
                                args: ast.args.map((child) => this._relativeToAbsolute(child)),
                            });
                    }
                case "UNARY_OPERATION":
                    return Object.assign({}, ast, {
                        right: this._relativeToAbsolute(ast.right),
                    });
                case "BIN_OPERATION":
                    return Object.assign({}, ast, {
                        right: this._relativeToAbsolute(ast.right),
                        left: this._relativeToAbsolute(ast.left),
                    });
            }
            return ast;
        }

        /**
         * return AST from an absolute PIVOT ast to a relative ast.
         *
         * Absolute PIVOT formulas use hardcoded ids while relative PIVOTS
         * formulas use the position
         *
         * e.g.
         * The following absolute formula
         *      `PIVOT("1","probability","product_id","37","bar","110")`
         * is converted to
         *      `PIVOT("1","probability","product_id",PIVOT.POSITION("1","product_id",0),"bar","110")`
         *
         * @param {Object} ast
         * @returns {Object}
         */
        _absoluteToRelative(ast) {
            switch (ast.type) {
                case "FUNCALL":
                    switch (ast.value) {
                        case "PIVOT":
                            return this._pivot_absoluteToRelative(ast);
                        case "PIVOT.HEADER":
                            return this._pivotHeader_absoluteToRelative(ast);
                        default:
                            return Object.assign({}, ast, {
                                args: ast.args.map((child) => this._absoluteToRelative(child)),
                            });
                    }
                case "UNARY_OPERATION":
                    return Object.assign({}, ast, {
                        right: this._absoluteToRelative(ast.right),
                    });
                case "BIN_OPERATION":
                    return Object.assign({}, ast, {
                        right: this._absoluteToRelative(ast.right),
                        left: this._absoluteToRelative(ast.left),
                    });
            }
            return ast;
        }

        /**
         * Convert a PIVOT.POSITION function AST to an absolute AST
         *
         * @see _relativeToAbsolute
         * @param {Object} ast
         * @returns {Object}
         */
        _pivotPositionToAbsolute(ast) {
            const [pivotIdAst, fieldAst, positionAst] = ast.args;
            const pivotId = JSON.parse(pivotIdAst.value);
            const fieldName = JSON.parse(fieldAst.value);
            const position = JSON.parse(positionAst.value);
            const values = this.getters.getPivotFieldValues(pivotId, fieldName);
            const id = values[position - 1];
            return {
                value: id ? `"${id}"` : `"#IDNOTFOUND"`,
                type: id ? "STRING" : "UNKNOWN",
            };
        }
        /**
         * Convert an absolute PIVOT.HEADER function AST to a relative AST
         *
         * @see _absoluteToRelative
         * @param {Object} ast
         * @returns {Object}
         */
        _pivotHeader_absoluteToRelative(ast) {
            ast = Object.assign({}, ast);
            const [pivotIdAst, ...domainAsts] = ast.args;
            if (pivotIdAst.type !== "STRING") return ast;
            ast.args = [pivotIdAst, ...this._domainToRelative(pivotIdAst, domainAsts)];
            return ast;
        }
        /**
         * Convert an absolute PIVOT function AST to a relative AST
         *
         * @see _absoluteToRelative
         * @param {Object} ast
         * @returns {Object}
         */
        _pivot_absoluteToRelative(ast) {
            ast = Object.assign({}, ast);
            const [pivotIdAst, measureAst, ...domainAsts] = ast.args;
            if (pivotIdAst.type !== "STRING") return ast;
            ast.args = [pivotIdAst, measureAst, ...this._domainToRelative(pivotIdAst, domainAsts)];
            return ast;
        }

        /**
         * Convert a pivot domain with hardcoded ids to a relative
         * domain with positions instead. Each domain element is
         * represented as an AST.
         *
         * e.g. (ignoring AST representation for simplicity)
         * The following domain
         *      "product_id", "37", "stage_id", "4"
         * is converted to
         *      "product_id", PIVOT.POSITION("#pivotId", "product_id", 15), "stage_id", PIVOT.POSITION("#pivotId", "stage_id", 3)
         *
         * @param {Object} pivotIdAst
         * @param {Object} domainAsts
         * @returns {Array<Object>}
         */
        _domainToRelative(pivotIdAst, domainAsts) {
            let relativeDomain = [];
            for (let i = 0; i <= domainAsts.length - 1; i += 2) {
                const fieldAst = domainAsts[i];
                const valueAst = domainAsts[i + 1];
                const pivotId = JSON.parse(pivotIdAst.value);
                const fieldName = JSON.parse(fieldAst.value);
                if (
                    this._isAbsolute(pivotId, fieldName) &&
                    fieldAst.type === "STRING" &&
                    ["STRING", "NUMBER"].includes(valueAst.type)
                ) {
                    const id = JSON.parse(valueAst.value);
                    const values = this.getters.getPivotFieldValues(pivotId, fieldName);
                    const index = values.indexOf(id.toString());
                    relativeDomain = relativeDomain.concat([
                        fieldAst,
                        {
                            type: "FUNCALL",
                            value: "PIVOT.POSITION",
                            args: [pivotIdAst, fieldAst, { type: "NUMBER", value: index + 1 }],
                        },
                    ]);
                } else {
                    relativeDomain = relativeDomain.concat([fieldAst, valueAst]);
                }
            }
            return relativeDomain;
        }

        _isAbsolute(pivotId, fieldName) {
            const field = this.getters.getPivotField(pivotId, fieldName.split(":")[0]);
            return field && field.type === "many2one";
        }

        /**
         * Remove pivot formulas with invalid ids.
         * i.e. pivot formulas containing "#IDNOTFOUND".
         *
         * Rows where all pivot formulas are invalid are removed, even
         * if there are others non-empty cells.
         * Invalid formulas next to valid ones (in the same row) are simply removed.
         */
        _removeInvalidPivotRows() {
            for (let sheet of this.getters.getSheets()) {
                const invalidRows = [];
                for (let rowIndex = 0; rowIndex < sheet.rows.length; rowIndex++) {
                    const { cells } = this.getters.getRow(sheet.id, rowIndex);
                    const [valid, invalid] = Object.values(cells)
                        .filter((cell) => cell.isFormula() && /^\s*=.*PIVOT/.test(cell.content))
                        .reduce(
                            ([valid, invalid], cell) => {
                                const isInvalid = /^\s*=.*PIVOT(\.HEADER)?.*#IDNOTFOUND/.test(cell.content);
                                return [
                                    isInvalid ? valid : valid + 1,
                                    isInvalid ? invalid + 1 : invalid,
                                ];
                            },
                            [0, 0]
                        );
                    if (invalid > 0 && valid === 0) {
                        invalidRows.push(rowIndex);
                    }
                }
                this.dispatch("REMOVE_COLUMNS_ROWS", {
                    dimension: "ROW",
                    elements: invalidRows,
                    sheetId: sheet.id,
                });
            }
            this._convertFormulas(this._getCells(/^\s*=.*PIVOT.*#IDNOTFOUND/), () => null);
        }
    }

    PivotTemplatePlugin.modes = ["headless"];
    PivotTemplatePlugin.getters = [];

    return PivotTemplatePlugin;
});
