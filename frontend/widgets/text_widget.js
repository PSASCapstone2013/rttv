function TextWidget(config) {
    Widget.call(this, config);

    $('.container').append("<script type=\"text/javascript\">document.getElementById('widget " + this.config.id + "').style.width=\"" + this.config.width + "px\";</script>");
    $('.container').append("<script type=\"text/javascript\">document.getElementById('widget " + this.config.id + "').style.height=\"" + this.config.height + "px\";</script>");

    var text = "",
        value_labels = {},
        divElement = document.getElementById('widget ' + this.config.id);

    if (this.config.controls) {
        this.config.controls.forEach(function(control) {
            value_labels[control.label] = ' ';
        });
    }

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
      return typeof n === 'number' && n % 1 !== 0;
    }
}

TextWidget.prototype = Object.create(Widget.prototype, {constructor: {value: TextWidget, enumerable: false, writable: true, configurable: true}});
