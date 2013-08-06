function Widget (config) {
    this.config = config;
    this.maxVal = 0;
    this.minVal = 99999;

    $('.container').append("<div class=\"widget " + this.config.id + "\" id=\"widget " + this.config.id + "\"></div>");
}

Widget.prototype = {
    putJSON: function(jsonObject) {
        var self = this;
        this.config.controls.forEach(function(control) {
            var self = this;
            // TODO bail if source does not cointain '.'
            var source = control.source.split('.');
            if (source[0] == jsonObject.fieldID) {
                var field = source[1];
                if (field in jsonObject) {
                    var value = eval('jsonObject.' + field);
                    // Check for the three built in config options for max, min & neg values
                    if (typeof source[2] != 'undefined') {
                        if (source[2] == 'Max') {
                            if (value > self.maxVal) { self.maxVal = value; }
                            value = self.maxVal;
                        }
                        if (source[2] == 'Min') {
                            if (value < self.minVal) { self.minVal = value; }
                            value = self.minVal;
                        }
                        if (source[2] == 'Neg') {
                            value = -value;
                        }
                    }
                    value = isFloat(value) ? value.toFixed(2) : value.toFixed(0);

                    // Convert to correct units
                    // Currently all possible input units are looked up in scripts/units.js
                    // Conversions are handled by scripts/quantities.js
                    if (field in unit) {
                        var outUnits = '';
                        var inUnits = unit[field];
                        var newValue = new Qty(value + inUnits);
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
    }
};
