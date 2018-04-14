$(document).ready(function () {

    $.getJSON('./data/data.json')
        .success(function (data) {
        console.log(data);

        const play_types = Object.keys(data);
        console.log(play_types);

        // const maxPoints = d3.max(data, function (d) { return d.pts; }),
        //     width = 1200,
        //     height = 500,
        //     column_width = width / 10,
        //     yScale = height / maxPoints;
        //
        // let svg = d3.select("#chart").append("svg")
        //     .attr("width", width)
        //     .attr("height", height)
        //     .attr("transform", "translate(0,0)");
        //
        // let games = svg.selectAll(".game")
        //     .data(data, function (d) {
        //         return [d.player, +d.pts, +d.index];
        //     }).enter()
        //     .append("circle")
        //     .attr("cx", function (d) {
        //         return (d.index * column_width) + (d.pts_count * 7) + 3.5;
        //     })
        //     .attr("cy", function (d) {
        //         return height - ((d.pts * yScale) - 3.5);
        //     })
        //     .attr("r", 3.5)
        //     .style("fill", "black")

    })
        .error(function (error, msg) {
            console.log(error);
            console.log(msg);
        });

});
