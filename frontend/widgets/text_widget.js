function TextWidget(_config) {
    $('.container').append("<div class=\"widget " + _config.id + "\" id=\"widget " + _config.id + "\"></div>");
    $('.container').append("<script type=\"text/javascript\">document.getElementById('widget " + _config.id + "').style.width=\"" + _config.width + "px\";</script>");
    $('.container').append("<script type=\"text/javascript\">document.getElementById('widget " + _config.id + "').style.height=\"" + _config.height + "px\";</script>");
    var self = this,
        text = "",
        config = _config,
        value_labels = {},
        divElement = document.getElementById('widget ' + config.id),
        maxval = 0, minval = 99999;
    
    if (config.controls) {
        config.controls.forEach(function(control) {
            value_labels[control.label] = " ";
        });
    }
    
    // TODO currently duplicated across all widgets... I want inheritence dammit!
    this.putJSON = function(jsonObject) {
        config.controls.forEach(function(control) {
            // TODO bail if source does not cointain '.'
            var source = control.source.split('.');
            if (source[0] == jsonObject.fieldID) {
                var field = source[1];
                if (field in jsonObject) {
                    var value = eval('jsonObject.' + field);
                    
                    // Check for the three built in config options for max, min & neg values
                    if (typeof source[2] != 'undefined') {
                        if (source[2] == 'Max') {
                            if (value > maxval) { maxval = value; }
                            value = maxval;
                        }
                        if (source[2] == 'Min') {
                            if (value < minval) { minval = value; }
                            value = minval;
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
    };
    
    this.put = function(controlLabel, value) {
        if (value_labels[controlLabel]) {
          value_labels[controlLabel] = value;
        }
        newText = '<strong>' + config.id + '</strong>';
        jQuery.each(value_labels, function(label, value) {
            newText += "<br>";
            newText += label + ': ';
            newText += value;
        });
        this.setText(newText);
    };
    
    this.setText = function(_text) {
        text = _text;
        divElement.innerHTML = text;
    };
    
    this.draw = function() {
    
    };
    
    function isFloat(n) {
      return typeof n === 'number' && n % 1 != 0;
    }
}
