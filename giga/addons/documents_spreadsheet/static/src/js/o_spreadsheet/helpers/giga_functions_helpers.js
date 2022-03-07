/** @giga-module **/

import spreadsheet from "../o_spreadsheet_loader";

const { parse } = spreadsheet;

/**
 * @typedef {Object} GigaFunctionDescription
 * @property {string} functionName Name of the function
 * @property {Array<string>} args Arguments of the function
 * @property {boolean} isPivot True if the function is relative to a Pivot
 * @property {boolean} isList True if the function is relative to a List
 */

/**
 * Get the first Pivot function description of the given formula.
 *
 * @param {string} formula
 *
 * @returns {GigaFunctionDescription|undefined}
 */
export function getFirstPivotFunction(formula) {
    return _getGigaFunctions(formula).find((fn) => fn.isPivot);
}

/**
 * Get the first List function description of the given formula.
 *
 * @param {string} formula
 *
 * @returns {GigaFunctionDescription|undefined}
 */
export function getFirstListFunction(formula) {
    return _getGigaFunctions(formula).find((fn) => fn.isList);
}

/**
 * Parse a spreadsheet formula and detect the number of PIVOT functions that are
 * present in the given formula.
 *
 * @param {string} formula
 *
 * @returns {number}
 */
export function getNumberOfPivotFormulas(formula) {
    return _getGigaFunctions(formula).filter((fn) => fn.isPivot).length;
}

/**
 * Parse a spreadsheet formula and detect the number of LIST functions that are
 * present in the given formula.
 *
 * @param {string} formula
 *
 * @returns {number}
 */
export function getNumberOfListFormulas(formula) {
    return _getGigaFunctions(formula).filter((fn) => fn.isList).length;
}

/**
 * This function is used to extract the Giga functions (PIVOT, LIST) from a
 * spreadsheet formula.
 *
 * @param {string} formula
 *
 * @private
 * @returns {Array<GigaFunctionDescription>}
 */
function _getGigaFunctions(formula) {
    let ast;
    try {
        ast = parse(formula);
    } catch (_) {
        return [];
    }
    return _getGigaFunctionsFromAST(ast);
}

/**
 * This function is used to extract the Giga functions (PIVOT, LIST) from an AST.
 *
 * @param {Object} AST (see o-spreadsheet)
 *
 * @private
 * @returns {Array<GigaFunctionDescription>}
 */
function _getGigaFunctionsFromAST(ast) {
    switch (ast.type) {
        case "UNARY_OPERATION":
            return _getGigaFunctionsFromAST(ast.right);
        case "BIN_OPERATION": {
            return _getGigaFunctionsFromAST(ast.left).concat(_getGigaFunctionsFromAST(ast.right));
        }
        case "FUNCALL": {
            const functionName = ast.value;
            if (["PIVOT", "PIVOT.HEADER", "PIVOT.POSITION"].includes(functionName)) {
                return [{ functionName, args: ast.args, isPivot: true }];
            } else if (["LIST", "LIST.HEADER"].includes(functionName)) {
                return [{ functionName, args: ast.args, isList: true }];
            } else {
                return ast.args.map((arg) => _getGigaFunctionsFromAST(arg)).flat();
            }
        }
        default:
            return [];
    }
}
