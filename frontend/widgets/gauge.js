function Gauge(config) {
    var self = this;

    this.value = 0;

    this.config = config;

    this.id = config.id || "guage";

    this.config.labelTextConfig = {
        size: Math.round(this.config.size / 9),
        x: this.config.size / 2,
        y: 3 * this.config.size / 10,
        anchor: "middle"
    };

    this.config.valueTextConfig = {
        size: Math.round(this.config.size / 10),
        x: this.config.size / 2,
        y: 4 * this.config.size / 5,
        anchor: "middle"
    };

    this.config.radius = this.config.size * 0.97 / 2;

    this.config.min = config.min || 0;
    this.config.max = config.max || 100;
    this.config.range = this.config.max - this.config.min;

    this.config.majorTicks = config.majorTicks || 5;
    this.config.minorTicks = config.minorTicks || 2;

    this.config.greenColor  = "#109618";
    this.config.yellowColor = "#FF9900";
    this.config.redColor    = "#DC3912";

    this.render = function() {

        this.svg = d3.select(".widget." + this.id).append("svg")
            .attr("class", "gauge")
            .attr("width", this.config.size)
            .attr("height", this.config.size)
            .style("background-color", "white");

        this.svg.append("circle")
        .attr("cx", this.config.size / 2)
        .attr("cy", this.config.size / 2)
        .attr("r", this.config.radius)
        .style("fill", "#ccc")
        .style("stroke", "#000")
        .style("stroke-width", "0.5px");

        this.svg.append("circle")
        .attr("cx", this.config.size / 2)
        .attr("cy", this.config.size / 2)
        .attr("r", 0.9 * this.config.radius)
        .style("fill", "#fff")
        .style("stroke", "#e0e0e0")
        .style("stroke-width", "2px");


        //this.drawBand(this.config.greenZones[index].from, this.config.greenZones[index].to, self.config.greenColor);

        var yellowFrom = (this.config.yellowPercent / 100.0) * this.config.max;
        var yellowTo = (this.config.redPercent / 100.0) * this.config.max;
        var redFrom = (this.config.redPercent / 100.0) * this.config.max;
        var redTo = this.config.max;

        this.drawBand(yellowFrom, yellowTo, self.config.yellowColor);

        this.drawBand(redFrom, redTo, self.config.redColor);

        this.appendText(this.svg, this.config.label, this.config.labelTextConfig);

        var majorDelta = this.config.range / (this.config.majorTicks - 1);
        for (var major = this.config.min; major <= this.config.max; major += majorDelta) {
            var minorDelta = majorDelta / this.config.minorTicks;
            for (var minor = major + minorDelta; minor < Math.min(major + majorDelta, this.config.max); minor += minorDelta) {
                var point1 = this.valueToPoint(minor, 0.75);
                var point2 = this.valueToPoint(minor, 0.85);

                this.svg.append("line")
                .attr("x1", point1.x)
                .attr("y1", point1.y)
                .attr("x2", point2.x)
                .attr("y2", point2.y)
                .style("stroke", "#666")
                .style("stroke-width", "1px");
            }

            var point1 = this.valueToPoint(major, 0.7);
            var point2 = this.valueToPoint(major, 0.85);

            this.svg.append("line")
            .attr("x1", point1.x)
            .attr("y1", point1.y)
            .attr("x2", point2.x)
            .attr("y2", point2.y)
            .style("stroke", "#333")
            .style("stroke-width", "2px");

            if (major == this.config.min || major == this.config.max) {
                var point = this.valueToPoint(major, 0.63);
                var refTextConfig = {
                    size: Math.round(this.config.size / 16),
                    x: point.x,
                    y: point.y,
                    anchor: major == this.config.min ? "start" : "end"
                };

                this.appendText(this.svg, major, refTextConfig);
            }
        }

        var pointerContainer = this.svg.append("g").attr("class", "pointerContainer");

        this.drawPointer(this.value);
        pointerContainer.append("circle")
        .attr("cx", this.config.size / 2)
        .attr("cy", this.config.size / 2)
        .attr("r", 0.12 * this.config.radius)
        .style("fill", "#4684EE")
        .style("stroke", "#666")
        .style("opacity", 1);
    };

    this.put = function(value) {
        this.value = value;
    };

    this.draw = function() {
        this.drawPointer(this.value);
    };

    this.drawBand = function(start, end, color) {
        if (0 >= end - start) return;

        this.svg.append("path")
        .style("fill", color)
        .attr("d", d3.svg.arc()
            .startAngle(this.valueToRadians(start))
            .endAngle(this.valueToRadians(end))
            .innerRadius(0.65 * this.config.radius)
            .outerRadius(0.85 * this.config.radius))
        .attr("transform", function() { return "translate(" + self.config.size / 2 + ", " + self.config.size / 2 + ") rotate(270)"; });
    };

    this.drawPointer = function(value) {
        var delta = this.config.range / 13,
            head = this.valueToPoint(value, 0.85),
            head1 = this.valueToPoint(value - delta, 0.12),
            head2 = this.valueToPoint(value + delta, 0.12),

            tailValue = value -  (this.config.range * (1/(270/360)) / 2),
            tail = this.valueToPoint(tailValue, 0.28),
            tail1 = this.valueToPoint(tailValue - delta, 0.12),
            tail2 = this.valueToPoint(tailValue + delta, 0.12),

            data = [head, head1, tail2, tail, tail1, head2, head],

            line = d3.svg.line()
                .x(function(d) { return d.x; })
                .y(function(d) { return d.y; })
                .interpolate("basis"),

            pointerContainer = this.svg.select(".pointerContainer"),
            pointer = pointerContainer.selectAll("path").data([data]);

        pointer.enter()
            .append("path")
            .attr("d", line)
            .style("fill", "#dc3912")
            .style("stroke", "#c63310")
            .style("fill-opacity", 0.7);

        pointer.transition()
            .attr("d", line)
            .ease("linear")
            .duration(100);

        var container =    pointerContainer.selectAll("text")
            .data([value])
            .text(Math.round(value))
            .enter();

        this.appendText(container, Math.round(value), this.config.valueTextConfig);
    };

    this.valueToDegrees = function(value) {
        return value / this.config.range * 270 - 45;
    };

    this.valueToRadians = function(value) {
        return this.valueToDegrees(value) * Math.PI / 180;
    };

    this.valueToPoint = function(value, factor) {
        var point = {
            x: this.config.size / 2 - this.config.radius * factor * Math.cos(this.valueToRadians(value)),
            y: this.config.size / 2 - this.config.radius * factor * Math.sin(this.valueToRadians(value))
        };

        return point;
    };

    this.appendText = function(obj, text, textConfig) {
        obj.append("text")
            .attr("x", textConfig.x)
            .attr("y", textConfig.y)
            .attr("dy", textConfig.size / 2)
            .attr("text-anchor", textConfig.anchor)
            .text(text)
            .style("font-size", textConfig.size + "px")
            .style("fill", "#333")
            .style("stroke-width", "0px");
    };
}
