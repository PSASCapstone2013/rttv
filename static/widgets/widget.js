var colors = d3.scale.category10().domain(d3.range(10));

function Widget (config) {
    var self = this;
    this.config = config;
    this.maxDataCount = 0;

    // track to-date min/max across ALL controls in this widget
    this.minValue = Number.MAX_VALUE;
    this.maxValue = Number.MIN_VALUE;
    this.config.controls.forEach(function(control, index) {
        var source = control.source.split('.');
        control.fieldID = source[0];
        control.field = source[1];
        control.valueTransformType = source[2]; // source[2] can be 'undefined', but that's handled in transformValue()
        // if color is not specified, provide a default from d3... text widgets have black text unless explicitly specified
        if (self.config.type != 'Text' && !control.color) {
            control.color = colors(index);
        }
        // each control has a unit. if not specified, provide a default.  if we can't find an appropriate default, make it empty
        control.units = control.units || ((control.field in unit) ? unit[control.field] : '');
        control.minValue = Number.MAX_VALUE;
        control.maxValue = Number.MIN_VALUE;
        control.dataCount = 0;
        control.value = 0;
    });

    $('.container').append("<div class=\"widget " + this.config.id + "\" id=\"widget " + this.config.id + "\"></div>");
    this.div = document.getElementById('widget ' + this.config.id);

}

Widget.prototype = {
    putJSON: function(jsonObject) {
        var self = this;
        this.config.controls.forEach(function(control) {
            if (control.fieldID == jsonObject.fieldID && control.field in jsonObject) {
                control.value = eval('jsonObject.' + control.field);
                control.value = self.transformValue(control);
                // Convert to correct units
                // Currently all possible input units are looked up in scripts/units.js
                // Conversions are handled by scripts/quantities.js
                if (control.field in unit && unit[control.field] != control.units) {
                    control.value = new Qty(control.value + ' ' + unit[control.field]).to(control.units).toPrec(0.01).scalar;
                }
                control.value = self.isFloat(control.value) ? control.value.toFixed(2) : control.value.toFixed(0);

                // keep track of the up-to-date min/max of this control
                control.minValue = Math.min(control.value, control.minValue);
                control.maxValue = Math.max(control.value, control.maxValue);
                // keep track of the up-to-date min/max of ALL controls in this widget
                self.minValue = Math.min(control.minValue, self.minValue);
                self.maxValue = Math.max(control.maxValue, self.maxValue);
                // keep track of the number of data points we receive, and the max of all controls in this widget
                self.maxDataCount = Math.max(++control.dataCount, self.maxDataCount);
                self.onControlChanged(control);
            }
        });
        self.draw();
    },

    draw: function() {}, // abstract
    onControlChanged: function(control) {}, // abstract

    /*
    * Transform types aappended to sources in the Yaml config file.
    * Ex:
    *_______________________________
    *   ...
    *   source: "GPS\x01.Height.Max"
    *   ...
    *_______________________________
    * Valid modifiers are: 'Max', 'Min' and 'Neg'
    */
    transformValue: function(control) {
        if (typeof control.valueTransformType == 'undefined') {
            return control.value;
        }
        switch(control.valueTransformType) {
            case 'Max':
            control.maxValue = Math.max(control.value, control.maxValue);
            return control.maxValue;
            case 'Min':
            control.minValue = Math.min(control.value, control.minValue);
            return control.minValue;
            case 'Neg':
            return -control.value;
            default:
            return control.value;
        }
    },

    isFloat: function(n) {
        return typeof n === 'number' && n % 1 !== 0;
    }
};
