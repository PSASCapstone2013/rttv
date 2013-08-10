function Widget (config) {
    this.config = config;
    this.minVal = 10000000.0;
    this.maxVal = -10000000.0;

    $('.container').append("<div class=\"widget " + this.config.id + "\" id=\"widget " + this.config.id + "\"></div>");
}

Widget.prototype = {
    putJSON: function(jsonObject) {
        var self = this;
        this.config.controls.forEach(function(control) {
            // TODO bail if source does not cointain '.'
            var source = control.source.split('.');
            if (source[0] == jsonObject.fieldID) {
                var field = source[1];
                if (field in jsonObject) {
                    var value = eval('jsonObject.' + field);
                    // Check for the three built in config options for max, min & neg values
                    value = self.transformValue(source[2], value);
                    value = self.isFloat(value) ? value.toFixed(2) : value.toFixed(0);

                    // Convert to correct units
                    // Currently all possible input units are looked up in scripts/units.js
                    // Conversions are handled by scripts/quantities.js
                    if (field in unit) {
                        var outUnits = '';
                        var inUnits = unit[field];
                        var newValue = new Qty(value + ' ' + inUnits);
                        if (typeof control.units != 'undefined') {
                          outUnits = control.units;
                          value = newValue.to(outUnits);
                          value = value.toPrec(0.01);
                        } else {
                          outUnits = unit[field];
                          value = newValue.to(outUnits);
                      }
                    }
                    self.put(control.label, value);
                }
            }
        });
    },

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
    transformValue: function(transformType, value) {
        if (typeof transformType == 'undefined') {
            return value;
        }
        switch(transformType) {
            case 'Max':
            this.maxVal = Math.max(value, this.maxVal);
            return this.maxVal;
            case 'Min':
            this.minVal = Math.min(value, this.minVal);
            return this.minVal;
            case 'Neg':
            return -value;
            default:
            return value;
        }
    },

    isFloat: function(n) {
      return typeof n === 'number' && n % 1 !== 0;
    }
};
