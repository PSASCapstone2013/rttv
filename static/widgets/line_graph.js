function LineGraph(config) {
    Widget.call(this, config);

    var labelMargin = {top: 10, right: 10, bottom: 20, left: 60},
        // default to 0 x/y domain, auto-scale as new data comes in
        xDomain = [0, 0],
        yDomain = [Number.MAX_VALUE, Number.MIN_VALUE],

        maxDataSize = this.config.maxDataSize || 100,
        mapX = d3.scale.linear().domain(xDomain).range([0, this.config.width]),
        mapY = d3.scale.linear().domain([0, 0]).range([this.config.height, 0]),

        xAxis = d3.svg.axis().scale(mapX).orient("bottom"),
        yAxis = d3.svg.axis().scale(mapY).orient("left"),

        svg = d3.select(".widget." + this.config.id).append("svg")
            .attr("width", this.config.width + labelMargin.left + labelMargin.right)
            .attr("height", this.config.height + labelMargin.top + labelMargin.bottom)
            .style("background-color", "white")
            .append("g")
            .attr("transform", "translate(" + labelMargin.left + "," + labelMargin.top + ")");

    svg.append("defs").append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", this.config.width)
        .attr("height", this.config.height);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + this.config.height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    var totalTextLength = 0;
    var delimiter = 5; // px between labels for different sources

    this.config.controls.forEach(function(control) {
        control.data = [];
        var line = d3.svg.line()
                    .x(function(d, i) { return mapX(xDomain[1] - i); })
                    .y(function(d)    { return mapY(d);              });
        control.path = new Path(svg, control.data, line, control.color);

        control.textElement = svg.append("text");
        control.textElement.attr("transform", "rotate(-90)").text(control.label + ' (' + control.units + ')');

        totalTextLength += control.textElement[0][0].getComputedTextLength();
    });

    var x = -config.height / 2 - totalTextLength / 2 - delimiter * (this.config.controls.length - 1);
    this.config.controls.forEach(function(control) {
        var textLength = control.textElement[0][0].getComputedTextLength();
        control.textElement
            .attr("y", -labelMargin.left)
            .attr("x", x)
            .attr("dy", "1em")
            .attr("stroke", control.color);

        x += textLength + delimiter;
    });

    this.onControlChanged = function(control) {
        // append the new value to the control's data series
        control.data.unshift(control.value);

        // "scale" (widen) domain until we reach the specified max-datapoints to have on the graph,
        // then start "translating" (keeping domain width, but tracking present data points)
        xDomain[1] = this.maxDataCount - 1;
        if (xDomain[1] >= maxDataSize) {
            xDomain[0] = xDomain[1] - maxDataSize;
        }

        // y-domain should contain all data points.
        yDomain[0] = Math.min(this.minValue, yDomain[0]);
        yDomain[1] = Math.max(this.maxValue, yDomain[1]);

        // remap to new x/y domains
        mapX.domain(xDomain);
        mapY.domain(yDomain);

        // update x/y-axis labels/ticks
        svg.select(".x.axis").call(xAxis);
        svg.select(".y.axis").transition().duration(100).call(yAxis);

    };

    // redraw path for each control
    this.draw = function() {
        this.config.controls.forEach(function(control) {
            control.path.draw();
        });
    };
}

LineGraph.prototype = Object.create(Widget.prototype, {constructor: {value: LineGraph, enumerable: false, writable: true, configurable: true}});

