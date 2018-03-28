function plot_shot_chart(data) {

    let courtSelection = d3.select("#shot-chart"),
        width = 500,
        height = .94 * width,
        yScale = d3.scaleLinear().domain([0, 47]).rangeRound([47, 0]);

    courtSelection.each(function (data) {
        // Responsive container for the shotchart
        d3.select(this).style("max-width", width / 16 + "em");
        d3.select(this).style("margin", "auto");
        // Select the SVG if it exists
        if (!d3.select(this).selectAll("svg").empty()) {
            let svg = d3.select(this).selectAll("svg");
        }
        else {
            let svg = d3.select(this).append("svg")
                .attr("viewBox", "0, 10, " + 50 + ", " + 43 + "")
                .classed("court", true);
            // Append the outer paint rectangle
            svg.append("g")
                .classed("court-paint", true)
                .append("rect")
                .attr("width", 16)
                .attr("height", 19)
                .attr("x", 25)
                .attr("transform", "translate(" + -8 + "," + 0 + ")")
                .attr("y", yScale(19));
            // Append inner paint lines
            svg.append("g")
                .classed("inner-court-paint", true)
                .append("line")
                .attr("x1", 19)
                .attr("x2", 19)
                .attr("y1", yScale(19))
                .attr("y2", yScale(0));
            svg.append("g")
                .classed("inner-court-paint", true)
                .append("line")
                .attr("x1", 31)
                .attr("x2", 31)
                .attr("y1", yScale(19))
                .attr("y2", yScale(0));
            // Append foul circle
            // Add clipPaths w/ rectangles to make the 2 semi-circles with our desired styles
            let solidFoulCircle = svg.append("g").classed("foul-circle solid", true);
            solidFoulCircle.append("defs").append("clipPath")
                .attr("id", "cut-off-bottom")
                .append("rect")
                .attr("width", 100)
                .attr("height", 6)
                .attr("x", 23)
                .attr("y", 27.9) /*foul line is 19 feet, then transform by 6 feet (circle radius) to pin rectangle above foul line..clip paths only render the parts of the circle that are in the rectangle path */
                .attr("transform", "translate(" + -6 + "," + -6 + ")");
            solidFoulCircle.append("circle")
                .attr("cx", 25)
                .attr("cy", yScale(19))
                .attr("r", 6)
                .attr("clip-path", "url(#cut-off-bottom)");
            // Add backboard and ri;
            svg.append("g").classed("backboard", true)
                .append("line")
                .attr("x1", 22)
                .attr("x2", 28)
                .attr("y1", yScale(4)) // 47-4
                .attr("y2", yScale(4)); // 47-4
            svg.append("g").classed("rim", true)
                .append("circle")
                .attr("cx", 25)
                .attr("cy", yScale(4.75)) // 47-4.75 need to set center point of circle to be 'r' above backboard
                .attr("r", .75); //regulation rim is 18 inches
            // Add restricted area -- a 4ft radius circle from the center of the rim
            var restrictedArea = svg.append("g").classed("restricted-area", true);
            restrictedArea.append("defs").append("clipPath")
                .attr("id", "restricted-cut-off")
                .append("rect")
                .attr("width", 10) // width is 2r of the circle it's cutting off
                .attr("height", 6.5) // height is 1r of the circle it's cutting off
                .attr("x", 24) // center rectangle
                .attr("y", 40)
                .attr("transform", "translate(" + -4 + "," + -4 + ")");
            restrictedArea.append("circle")
                .attr("cx", 25)
                .attr("cy", yScale(4.75))
                .attr("r", 4)
                .attr("clip-path", "url(#restricted-cut-off)");
            // Add 3 point arc
            let threePointArea = svg.append("g").classed("three-point-area", true);
            threePointArea.append("defs").append("clipPath")
                .attr("id", "three-point-cut-off")
                .append("rect")
                .attr("width", 44)
                .attr("height", 23.75)
                .attr("x", 25)
                .attr("y", yScale(6)) // put recentagle at centerpoint of circle then translate by the inverse of the circle radius to cut off top half
                .attr("transform", "translate(" + -22 + "," + -23.75 + ")");
            threePointArea.append("circle")
                .attr("cx", 25)
                .attr("cy", yScale(4.75))
                .attr("r", 23.75)
                .attr("clip-path", "url(#three-point-cut-off)");
            threePointArea.append("line")
                .attr("x1", 3.12)
                .attr("x2", 3.12)
                .attr("y1", 32.8)
                .attr("y2", yScale(0));
            threePointArea.append("line")
                .attr("x1", 46.9)
                .attr("x2", 46.9)
                .attr("y1", 32.8)
                .attr("y2", yScale(0));
            // Append baseline
            svg.append("g")
                .classed("court-baseline", true)
                .append("line")
                .attr("x1", 0)
                .attr("x2", 50)
                .attr("y1", yScale(0))
                .attr("y2", yScale(0));

            svg.append("g").classed("shots", true);
        }
    });

}
