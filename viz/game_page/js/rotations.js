function plot_rotation_heat_map(rotation_data, score_data) {

    var margin = {top: 30, right: 150, bottom: 30, left: 350},
        width = 1700 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

    var svg = d3.select("#chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    rotation_data.sort(function (a, b) {
        if (a.pindex === b.pindex)
            return 0;
        if (a.pindex < b.pindex)
            return -1;
        if (a.pindex > b.pindex)
            return 1;
    });

    var players = [],
        previous_pindex = 0,
        max_minute = 0,
        top_team_player_count = 0,
        max_pindex = 0;

    $.each(rotation_data, function (i, d) {
        if ($.inArray(this.player, players) === -1) {
            if (this.pindex - previous_pindex > 1) {
                players.push("");
                top_team_player_count = this.pindex - 2;
            }
            players.push(this.player);
        }
        previous_pindex = this.pindex;

        if (this.pindex > max_pindex) {
            max_pindex = this.pindex;
        }

        if (+this.end_time > max_minute) {
            max_minute = +this.end_time;
        }
    });

    max_minute = max_minute / 60;

    var rect_height = Math.floor(height / (max_pindex + 2)),
        bot_team_player_count = (players.length - 1) - top_team_player_count,
        x_scale = (width - margin.right) / (max_minute * 60);

    svg.selectAll(".playerLabel")
        .data(players)
        .enter().append("text")
        .text(function (d) {
            return d;
        })
        .attr("x", 0)
        .attr("y", function (d, i) {
            return (i * rect_height);
        })
        .style("text-anchor", "end")
        .attr("transform", "translate(-6," + rect_height / 1.5 + ")")
        .attr("class", "dayLabel axis axis-workweek");

    var minutes = ["Q1", "", "", "", "", "", "", "", "", "", "", "", "Q2", "", "", "", "", "", "", "", "", "", "", "",
        "Q3", "", "", "", "", "", "", "", "", "", "", "", "Q4", "", "", "", "", "", "", "", "", "", ""];
    if (max_minute >= 48) {
        var extra_minutes = max_minute - 48;
        minutes.push("");
        for (var i = 0; i < extra_minutes; i++) {
            if (i % 5 === 0) {
                minutes.push("OT" + (i / 5 + 1));
            }
            else {
                minutes.push("");
            }
        }
    }
    minutes.push('end');

    svg.selectAll(".timeLabel")
        .data(minutes)
        .enter().append("text")
        .text(function (d) {
            return d;
        })
        .attr("x", function (d, i) {
            return (i * 60 * x_scale);
        })
        .attr("y", 0)
        .style("text-anchor", "middle")
        .attr("transform", "translate(" + (rect_height / 2) + ", -6)")
        .attr("class", "timeLabel mono axis axis-worktime");

    svg.selectAll(".timeLabel2")
        .data(minutes)
        .enter().append("text")
        .text(function (d) {
            return d;
        })
        .attr("x", function (d, i) {
            return (i * 60 * x_scale);
        })
        .attr("y", (max_pindex + 1) * rect_height)
        .style("text-anchor", "middle")
        .attr("transform", "translate(" + (rect_height / 2) + ", -6)")
        .attr("class", "timeLabel mono axis axis-worktime");


    var cards = svg.selectAll(".hour")
        .data(rotation_data, function (d) {
            return d.pindex + ':' + d.minute;
        });

    cards.append("title");

    cards.enter().append("rect")
        .attr("x", function (d) {
            return d.start_time * x_scale;
        })
        .attr("y", function (d) {
            return (d.pindex - 1) * rect_height;
        })
        .attr("rx", 1)
        .attr("ry", 1)
        .attr("class", "hour bordered")
        .attr("width", function (d) {
            return (d.end_time - d.start_time) * x_scale;
        })
        .attr("height", rect_height - 4)
        .style("fill", 'black');

    cards.select("title").text(function (d) {
        return d.value;
    });

    cards.exit().remove();

    var max_lead = 0;

    $.each(score_data, function (i, d) {
        if (Math.abs(this.score_margin) > max_lead) {
            max_lead = Math.abs(this.score_margin);
        }
    });

    var yAxisShiftBool = bot_team_player_count < top_team_player_count,
        yAxisScale = (((Math.min(top_team_player_count, bot_team_player_count) * 2) + 1) * rect_height),
        yAxisShift = yAxisShiftBool ? ((Math.abs(top_team_player_count - bot_team_player_count)) * rect_height) - margin.top: -margin.bottom;

    var x = d3.scaleLinear()
        .rangeRound([margin.left, width + margin.left - margin.right]);

    var y = d3.scaleLinear()
        .range([-margin.top, yAxisScale - margin.bottom]);

    var line = d3.line()
        .x(function (d) {
            return x(d.minute);
        })
        .y(function (d) {
            return y(d.score_margin);
        })
        .curve(d3.curveStep);

    x.domain(d3.extent(score_data, function (d) {
        return +d.minute;
    }));

    y.domain([max_lead, -max_lead]);

    svg.append("g")
        .call(d3.axisRight(y))
        .attr("transform", "translate(" + ((max_minute * x_scale * 60) + 5) + ", " + (margin.bottom + margin.top + yAxisShift) + ")")
        .append("text")
        .attr("fill", "#000")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")

    svg.append("path")
        .datum(score_data)
        .attr("class", "point-diff")
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-opacity", 1)
        .attr("stroke-linejoin", "bevel")
        .attr("stroke-linecap", "square")
        .attr("stroke-width", 3.5)
        .attr("d", line)
        .attr("transform", "translate(" + -margin.left + "," + (margin.bottom + margin.top + yAxisShift) + ")");

    var stroke_width = 2,
        stroke_opacity = 0.25,
        stroke_color = 'black';

    for (i = 0; i < 4; i++) {
        svg.append("line")
            .attr("x1", 720 * i * x_scale)
            .attr("x2", 720 * i * x_scale)
            .attr("y1", 0)
            .attr("y2", rect_height * (max_pindex))
            .style("stroke-width", stroke_width)
            .attr("stroke-opacity", stroke_opacity)
            .style("stroke", stroke_color)
            .style("fill", 'none');
    }

    console.log((max_minute - 48) / 5);

    if (max_minute > 48) {
        for (i = 0; i < ((max_minute - 48) / 5); i++) {
            console.log(i);
            svg.append("line")
                .attr("x1", (2880 + (300 * i)) * x_scale)
                .attr("x2", (2880 + (300 * i)) * x_scale)
                .attr("y1", 0)
                .attr("y2", rect_height * (max_pindex))
                .style("stroke-width", stroke_width)
                .attr("stroke-opacity", stroke_opacity)
                .style("stroke", stroke_color)
                .style("fill", 'none');
        }
    }

    svg.append("line")
        .attr("x1", 0)
        .attr("x2", width - margin.right)
        .attr("y1", (top_team_player_count + 0.5) * rect_height )
        .attr("y2", (top_team_player_count + 0.5) * rect_height )
        .style("stroke-width", stroke_width)
        .attr("stroke-opacity", stroke_opacity)
        .style("stroke", stroke_color)
        .style("fill", 'none');
}
