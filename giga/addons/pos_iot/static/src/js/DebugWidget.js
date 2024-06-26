giga.define('pos_restaurant.DebugWidget', function(require) {
    'use strict';

    const DebugWidget = require('point_of_sale.DebugWidget');
    const Registries = require('point_of_sale.Registries');

    const PosIotDebugWidget = DebugWidget =>
        class extends DebugWidget {
            /**
             * @override
             */
            refreshDisplay(event) {
                event.preventDefault();
                if (this.env.pos.iot_device_proxies.display) {
                    this.env.pos.iot_device_proxies.display.action({ action: 'display_refresh' });
                }
            }
        };

    Registries.Component.extend(DebugWidget, PosIotDebugWidget);

    return DebugWidget;
});
