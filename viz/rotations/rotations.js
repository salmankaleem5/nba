$(document).ready(function () {
    const margin = {top: 40, right: 150, bottom: 30, left: 170},
        width = 1200 - margin.left - margin.right,
        height = 510 - margin.top - margin.bottom,
        playerColors = colorbrewer.Greys[9];

    let gridSize = Math.floor(width / 48),
        legendElementWidth = gridSize * 3,
        buckets = 9;

    let svg = d3.select("#chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    $.getJSON('./rotations.json', function (rotation_data) {

        console.log(rotation_data);

        rotation_data.sort(function (a, b) {
            if (a.pindex === b.pindex)
                return 0;
            if (a.pindex < b.pindex)
                return -1;
            if (a.pindex > b.pindex)
                return 1;
        });

        let players = [],
            previous_pindex = 0;

        $.each(rotation_data, function (i, d) {
            if ($.inArray(this.player, players) === -1) {
                players.push(this.player);
            }
            previous_pindex = this.pindex;
        });

        svg.selectAll(".playerLabel")
            .data(players)
            .enter().append("text")
            .text(function (d) {
                return d;
            })
            .attr("x", 0)
            .attr("y", function (d, i) {
                return (i * gridSize);
            })
            .style("text-anchor", "end")
            .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
            .attr("class", "dayLabel axis axis-workweek");

        let minutes = ["Q1", "", "", "", "", "", "", "", "", "", "", "", "Q2", "", "", "", "", "", "", "", "", "", "",
            "", "Q3", "", "", "", "", "", "", "", "", "", "", "", "Q4", "", "", "", "", "", "", "", "", "", "", "end"];

        svg.selectAll(".timeLabel")
            .data(minutes)
            .enter().append("text")
            .text(function (d) {
                return d;
            })
            .attr("x", function (d, i) {
                return (i * gridSize);
            })
            .attr("y", 0)
            .style("text-anchor", "middle")
            .attr("transform", "translate(" + (gridSize - 13) * 2 + ", -6)")
            .attr("class", "timeLabel mono axis axis-worktime");

        let playerColorScale = d3.scaleQuantile()
            .domain([0, buckets - 1, d3.max(rotation_data, function (d) {
                return d.value;
            })])
            .range(playerColors);

        let cards = svg.selectAll(".hour")
            .data(rotation_data, function (d) {
                return d.pindex + ':' + d.minute;
            });

        cards.append("title");

        cards.enter().append("rect")
            .attr("x", function (d) {
                return (d.minute - 1) * gridSize;
            })
            .attr("y", function (d) {
                return (d.pindex - 1) * gridSize;
            })
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("class", "hour bordered")
            .attr("width", gridSize)
            .attr("height", gridSize)
            .attr("opacity", function (d1) {
                return (d1.value  / d3.max(rotation_data, function (d2) {return d2.value;}));
            })
            .style("fill", "black");

        cards.select("title").text(function (d) {
            return d.value;
        });

        cards.exit().remove();

        let legend = svg.selectAll(".legend")
            .data([0].concat(playerColorScale.quantiles()), function (d) {
                return d;
            });

        let legend_y_shift = 0;

        legend.enter().append("g")
            .attr("class", "legend")
            .append("rect")
            .attr("x", function (d, i) {
                return legendElementWidth * i;
            })
            .attr("y", height - legend_y_shift)
            .attr("width", legendElementWidth)
            .attr("height", gridSize)
            .style("fill", function (d, i) {
                return playerColors[i];
            });

        legend.enter().append("text")
            .style("fill", function (d) {
                return playerColorScale(d < 30 ? 60 : 0);
            })
            .text(function (d, i) {
                return " ≥ " + Math.round(d);
            })
            .attr("x", function (d, i) {
                return legendElementWidth * i;
            })
            .attr("y", height + gridSize - legend_y_shift - 3)
            .attr("class", "legend");

        svg.selectAll(".legendLabel")
            .data(["Seconds Played in Minute"])
            .enter()
            .append("text")
            .text(function (d) {
                return d;
            })
            .attr("y", height + gridSize - (legend_y_shift + 3))
            .attr("x", function () {
                return (legend.enter().data().length * legendElementWidth) + 5
            })
            .attr("class", "legend");

        legend.exit().remove();
    });
});
