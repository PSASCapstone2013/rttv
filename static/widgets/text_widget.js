function TextWidget(config) {
    Widget.call(this, config);

    $('.container').append("<script type=\"text/javascript\">document.getElementById('widget " + this.config.id + "').style.width=\"" + this.config.width + "px\";</script>");
    $('.container').append("<script type=\"text/javascript\">document.getElementById('widget " + this.config.id + "').style.height=\"" + this.config.height + "px\";</script>");

    this.onControlChanged = function(control) {
        var text = '<strong>' + config.id + '</strong>';
        this.config.controls.forEach(function(control) {
            text += "<br>";
            text += control.label + ': ' + control.value + ' ' + control.units;
        });
        this.setText(text);
    };

    this.setText = function(text) {
        this.div.innerHTML = text;
    };
}

TextWidget.prototype = Object.create(Widget.prototype, {constructor: {value: TextWidget, enumerable: false, writable: true, configurable: true}});