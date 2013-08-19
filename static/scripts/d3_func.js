function Path(svg, data, generatorFunction, color) {

    var path = svg.append('path')
        .attr('clip-path', 'url(#clip)')
        .data([data])
        .attr('stroke', color)
        .attr('fill', 'none')
        .attr('stroke-width', 1.5);

    // redraw the path
    this.draw = function() {
        path.attr('d', generatorFunction);
    };
}

// returns an array of :size zeros. ex: zeros(3) => [0, 0, 0]
function zeros(size) {
    return d3.range(size).map(function() { return 0; });
}
