function Widget (config) {
    this.config = config;

    this.maxVal = 0;
    this.minVal = 99999;

    var self = this;
    $('.container').append("<div class=\"widget " + this.config.id + "\" id=\"widget " + this.config.id + "\"></div>");
}

Widget.prototype = {
    putJSON: function(jsonObject) {
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

                    if (isFloat(value)) {
                        value = value.toFixed(2);
                    }
                    else {
                      value = value.toFixed(0);
                    }

                    // Convert to correct units
                    // Currently all possible input units are looked up in scripts/units.js
                    // Conversions are handled by scripts/quantities.js
                    var outUnits = '';
                    if (typeof control.units != 'undefined' && field in unit) {
                      var inUnits = unit[field];
                      outUnits = control.units;

                      var newValue = new Qty(value + inUnits);
                      value = newValue.to(outUnits);
                      value = value.toPrec(0.01);
                    }
                    else if (field in unit) {
                      outUnits = unit[field];
                      value = newValue.to(outUnits);
                    }

                    self.put(control.label, value);
                }
            }
        });
    }
};