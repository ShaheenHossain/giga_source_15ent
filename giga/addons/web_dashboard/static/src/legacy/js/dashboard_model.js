giga.define('web_dashboard.DashboardModel', function (require) {
"use strict";

/**
 * This module defines the DashboardModel, an extension of the BasicModel.
 * Unlike the BasicModel, the DashboardModel only keep a single dataPoint (there
 * is no relational data in this model), and this dataPoint contains two
 * additional keys: aggregates and formulas, which gather the information
 * about the <aggregate> and <formula> occurrences in the dashboard arch.
 */

var BasicModel = require('web.BasicModel');
var dataComparisonUtils = require('web.dataComparisonUtils');
var Domain = require('web.Domain');
var pyUtils = require('web.py_utils');

var computeVariation = dataComparisonUtils.computeVariation;

var DashboardModel = BasicModel.extend({

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    __get: function () {
        var record = this._super.apply(this, arguments);
        record.timeRanges = this.dataPoint.timeRanges;
        record.timeRange = this.dataPoint.timeRange;
        record.comparisonTimeRange = this.dataPoint.comparisonTimeRange;
        record.compare = this.dataPoint.compare;
        record.comparisonData = this.dataPoint.comparisonData;
        record.variationData = this.dataPoint.variationData;
        record.isSample = this.isSampleModel;
        return record;
     },
    /**
     * @override
     */
    __load: function (params) {
        params.type = 'record';
        this.dataPoint = this._makeDataPoint(params);
        return this._load(this.dataPoint);
    },
    /**
     * @override
     */
    __reload: function (id, options) {
        options = options || {};
        if (options.domain !== undefined) {
            this.dataPoint.domain = options.domain;
        }
        if ('timeRanges' in options) {
            this._processTimeRanges(this.dataPoint, options.timeRanges);
        }
        return this._load(this.dataPoint);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Evaluates formulas of the dataPoint with its values.
     *
     * @private
     * @param {Object} dataPoint
     */
    _evaluateFormulas: function (dataPoint) {
        _.each(dataPoint.formulas, function (formula, formulaID) {
            try {
                dataPoint.data[formulaID] = pyUtils.py_eval(formula.value, {
                    record: dataPoint.data
                });
                if (!isFinite(dataPoint.data[formulaID])) {
                    dataPoint.data[formulaID] = NaN;
                }
            } catch (e) {
                dataPoint.data[formulaID] = NaN;
            }
            if (dataPoint.compare) {
                try {
                    dataPoint.comparisonData[formulaID] = pyUtils.py_eval(formula.value, {
                        record: dataPoint.comparisonData
                    });
                    if (!isFinite(dataPoint.comparisonData[formulaID])) {
                        dataPoint.comparisonData[formulaID] = NaN;
                    }
                } catch (e) {
                    dataPoint.comparisonData[formulaID] = NaN;
                }
            }
        });
    },
    /**
     * @param  {Array[]} aggregateDomain
     * @param  {Array[]} range
     * @return {Array[]}
     */
    _getReadGroupDomain: function (aggregateDomain, range) {
        return Domain.prototype.normalizeArray(this.dataPoint.domain)
            .concat(range)
            .concat(Domain.prototype.normalizeArray(new Domain(aggregateDomain).toArray()));
    },
    /**
     * @override
     */
    _isEmpty() {
        return this.dataPoint.count === 0;
    },
    /**
     * @override
     * @private
     */
    _load: function (dataPoint) {
        var self = this;

        let count = 0;
        const domainMapping = {};
        if (this.useSampleModel) {
            // force to do a read_group RPC without domain to determine if there is data to display
            domainMapping['[]'] = [];
        }
        var fieldsInfo = dataPoint.fieldsInfo.dashboard;
        _.each(dataPoint.aggregates, function (aggregateName) {
            var domain = fieldsInfo[aggregateName].domain;
            if (domain in domainMapping) {
                domainMapping[domain].push(aggregateName);
            } else {
                domainMapping[domain] = [aggregateName];
            }
        });

        var defs = [];
        _.each(domainMapping, function (aggregateNames, domain) {
            var fields = _.map(aggregateNames, function (aggregateName) {
                var fieldName = fieldsInfo[aggregateName].field;
                var groupOperator = fieldsInfo[aggregateName].group_operator;
                return aggregateName + ':' + groupOperator + '(' + fieldName + ')';
            });

            defs.push(self._readGroup({
                domain: self._getReadGroupDomain(domain, self.dataPoint.timeRange),
                fields: fields,
            }).then(function (result) {
                count = count + (domain === '[]' ? result.__count : 0);
                _.extend(self.dataPoint.data, _.pick(result, aggregateNames));
            }));
            if (dataPoint.compare) {
                defs.push(self._readGroup({
                    domain: self._getReadGroupDomain(domain, self.dataPoint.comparisonTimeRange),
                    fields: fields,
                }).then(function (result) {
                    count = count + (domain === '[]' ? result.__count : 0);
                    _.extend(self.dataPoint.comparisonData, _.pick(result, aggregateNames));
                }));
            }
        });

        return Promise.all(defs).then(function () {
            self.dataPoint.count = count;
            self._evaluateFormulas(dataPoint);
            if (dataPoint.compare) {
                var value, comparisonValue;
                for (var statisticName in dataPoint.data) {
                    value = dataPoint.data[statisticName];
                    comparisonValue = dataPoint.comparisonData[statisticName];
                    dataPoint.variationData[statisticName] = computeVariation(value, comparisonValue);
                }
            } else {
                dataPoint.comparisonData = {};
                dataPoint.variationData = {};
            }
            return dataPoint.id;
        });
    },
    /**
     * @override
     * @private
     */
    _makeDataPoint: function (params) {
        var dataPoint = this._super.apply(this, arguments);
        dataPoint.aggregates = params.aggregates;
        dataPoint.count = 0;
        dataPoint.formulas = params.formulas;
        dataPoint.comparisonData = {};
        dataPoint.variationData = {};
        this._processTimeRanges(dataPoint, params.timeRanges);
        return dataPoint;
    },
    /**
     * @param  {Object} args
     * @returns {Promise}
     */
    _readGroup: function (args) {
        var readGroupArgs = _.extend({
            context: this.dataPoint.getContext(),
            groupBy: [],
            lazy: true,
            method: 'read_group',
            model: this.dataPoint.model,
            orderBy: [],
        }, args);
        return this._rpc(readGroupArgs).then(function (result) {
            result = result[0];
            return _.mapObject(result, function (value) {
                return value || 0;
            });
        });
    },
    _processTimeRanges: function (dataPoint, timeRanges) {
        const { range, comparisonRange } = timeRanges;
        dataPoint.timeRanges = timeRanges;
        dataPoint.timeRange = range || [];
        dataPoint.comparisonTimeRange = comparisonRange || [];
        dataPoint.compare = Boolean(dataPoint.comparisonTimeRange.length);
    },
});

return DashboardModel;

});
