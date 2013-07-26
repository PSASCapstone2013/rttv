var color = d3.scale.category10();
  
function Path(svg, data, generatorName, generatorFunction) {

    var path = svg.append("g")
        .attr("clip-path", "url(#clip)")
        .append("path")
        .data([data])
        .attr("class", generatorName);

    // redraw the path
    this.draw = function(translate) {
        path.attr("d", generatorFunction)
         .attr("transform", "translate(0)")
         .transition()
         .attr("transform", "translate(" + translate + ")");
    };
}

function zeros(size) {
    return d3.range(size).map(function() { return 0; });
}

function tick() {
  widgets.forEach(function(widget) {
    widget.draw();
  });
}
