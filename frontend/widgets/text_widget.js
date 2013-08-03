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
                if (source[1] in jsonObject) {
                    var value = eval('jsonObject.' + source[1]);
                    // Check for the two built in config options for max and min values
                    if (typeof source[2] != 'undefined') {
                        if (source[2] == 'Max') {
                            if (value > maxval) { maxval = value; }
                            value = maxval;
                        }
                        if (source[2] == 'Min') {
                            if (value < minval) { minval = value; }
                            value = minval;
                        }
                    }
                    self.put(control.label, value);
                }
            }
        });
    };
    
    this.put = function(controlLabel, value) {
        if (value_labels[controlLabel]) {
        	if (isFloat(value)) {
              value_labels[controlLabel] = value.toFixed(2);
          }
          else {
          	value_labels[controlLabel] = value.toFixed(0);
          }
        }
        newText = '<strong>' + config.id.toUpperCase() + '</strong>';
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
