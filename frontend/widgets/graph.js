function Graph(width, height, maxDataSize) {

    var dataCount = 0, // keep track of the number of data points we receive
                       // when we reach maxDataSize, we stop scaling x-axis and start scrolling
        data = zeros(maxDataSize),

        labelMargin = {top: 10, right: 10, bottom: 20, left: 60};
        // default to 0 x/y domain, auto-scale as new data comes in
        xDomain = [0, 0],
        yDomain = [Number.MAX_VALUE, Number.MIN_VALUE],

        mapX = d3.scale.linear().domain(xDomain).range([0, width]),
        mapY = d3.scale.linear().domain([0, 0]).range([height, 0]),

        xAxis = d3.svg.axis().scale(mapX).orient("bottom"),
        yAxis = d3.svg.axis().scale(mapY).orient("left"),

        line = d3.svg.line()
        .x(function(d, i) { return mapX(xDomain[1] - i); })
        .y(function(d) { return mapY(d); }),

        area = d3.svg.area()
        .x(function(d, i) { return mapX(xDomain[1] - i); })
        .y0(height)
        .y1(function(d) { return mapY(d); }),

        svg = d3.select("body").append("svg")
            .attr("width", width + labelMargin.left + labelMargin.right)
            .attr("height", height + labelMargin.top + labelMargin.bottom)
            .style("background-color", "white")
            .append("g")
            .attr("transform", "translate(" + labelMargin.left + "," + labelMargin.top + ")"),
        paths = [new Path(svg, data, "line", line),
                 new Path(svg, data, "area", area)];

    svg.append("defs").append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", width)
        .attr("height", height);

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
    .attr("class", "y axis")
        .call(yAxis);

    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -labelMargin.left)
        .attr("x", -height / 2)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Z Roll");

    // add data to the list
    this.put = function(value) {
        // pop the old data point off the front
        data.pop();

        data.unshift(value);

        // "scale" (widen) domain until we reach the specified max-datapoints to have on the graph,
        // then start "translating" (keeping domain width, but tracking present data points)
        xDomain[1] = ++dataCount;
        if (dataCount >= maxDataSize) {
            xDomain[0] = xDomain[1] - maxDataSize;
        }
        // y-domain should contain all data points.
        yDomain[0] = Math.min(value, yDomain[0]);
        yDomain[1] = Math.max(value, yDomain[1]);

        // remap to new x/y domains
        mapX.domain(xDomain);
        mapY.domain(yDomain);

        // update x/y-axis labels/ticks
        svg.select(".x.axis").call(xAxis);
        svg.select(".y.axis").transition().duration(100).call(yAxis);

    };

    // redraw each path (line & area)
    this.draw = function() {
        paths.forEach(function(path) {
            path.draw(0);
        });
    };
}
