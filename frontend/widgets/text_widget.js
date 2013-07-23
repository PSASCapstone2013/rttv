function TextWidget(_config) {
    $('.container').append("<div class=\"widget " + _config.id + "\" id=\"widget " + _config.id + "\"></div>");
    var self = this,
        text = "",
        config = _config,
        value_labels = {},
        divElement = document.getElementById('widget ' + config.id);

    if (config.controls) {
        config.controls.forEach(function(control) {
            value_labels[control.label] = "";
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
                    self.put(control.label, value);
                }
            }
        });
    };

    this.put = function(controlLabel, value) {
        if (value_labels[controlLabel]) {
            value_labels[controlLabel] = value.toFixed(2);
        }
        newText = '<strong>' + config.id + '</strong>';
        value_labels.forEach(function(value_label) {
            newText += "<br>";
            newText += value_label + ': ';
            newText += value_labels[value_label];
        });
        this.setText(newText);
    };

    this.setText = function(_text) {
        text = _text;
        divElement.innerHTML = text;
    };

    this.draw = function() {

    };
}
