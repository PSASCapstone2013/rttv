function Widget (config) {
    this.config = config;

    this.config.controls.forEach(function(control) {
        var source = control.source.split('.');
        control.fieldID = source[0];
        control.field = source[1];
        control.valueTransformType = source[2]; // this can be 'undefined', but that's handled in transformValue()
        control.minValue = Number.MAX_VALUE;
        control.maxValue = Number.MIN_VALUE;
        control.value = 0;
        if (typeof control.units == 'undefined') {
            // ensure control.units is defined. if we can't find an appropriate unit, make it empty
            control.units = (control.field in unit) ? unit[control.field] : '';
        }
    });

    if (typeof this.config.column == 'undefined') {
      $('.container').append("<div class=\"widget " + this.config.id + "\" id=\"widget " + this.config.id + "\"></div>");
    }
    else {
      $('#' + this.config.column).append("<div class=\"widget " + this.config.id + "\" id=\"widget " + this.config.id + "\"></div>");
    }
    this.div = document.getElementById('widget ' + this.config.id);

    var self = this;
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
