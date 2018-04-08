var team_colors = {
        'NOP': ['#0C2340', '#C8102E', '#85714D'],
        'HOU': ['#CE1141', '#FDB927'],
        'CLE': ['#6F2633', '#FFB81C'],
        'BKN': ['#000000', '#FFFFFF'],
        'MIN': ['#002B5C', '#7AC143'],
        'MEM': ['#7D9BC1', '#FFC72C'],
        'NYK': ['#F58426', '#006BB6'],
        'CHA': ['#00788C', '#1D1160', '#888B8D'],
        'POR': ['#E13A3E', '#000000'],
        'LAC': ['#ED174C', '#006BB6'],
        'PHX': ['#E56020', '#1D1160'],
        'MIA': ['#98012e', '#faa11b'],
        'PHI': ['#003DA5', '#D50032']
    };

function get_color_contrast(hex1, hex2) {
    let rgb1 = [parseInt(hex1.substr(1,3), 16), parseInt(hex1.substr(3,5), 16), parseInt(hex1.substr(5,7), 16)],
        rgb2 = [parseInt(hex2.substr(1,3), 16), parseInt(hex2.substr(3,5), 16), parseInt(hex2.substr(5,7), 16)];

    return (Math.abs(rgb1[0] - rgb2[0]) + Math.abs(rgb1[1] - rgb2[1]) + Math.abs(rgb1[2] - rgb2[2]));
}

function get_colors(home_abb, away_abb) {
  for (let ix=0; ix < team_colors[home_abb].length; ix++) {
    for (let jx=0; jx < team_colors[away_abb].length; jx++) {
          if (get_color_contrast(team_colors[home_abb][ix], team_colors[away_abb][jx]) > 40000) {
              return [team_colors[home_abb][ix], team_colors[away_abb][jx]];
            }
        };
    };
}

function plot_rotation_heat_map(rotation_data, score_data, home_abb, away_abb) {

    let colors = get_colors(home_abb, away_abb);
    let home_color = colors[0],
        away_color = colors[1];

    var max_width = 1500;
    var hor_margin_scale = Math.min($(window).width(), max_width) / 1500;

    var margin = {top: 30, right: 50 * hor_margin_scale, bottom: 30, left: 200 * hor_margin_scale},
        width = Math.min($(window).width(), max_width) - margin.left - margin.right,
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
        .attr("height", rect_height - 5)
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

    y.domain([max_lead, -max_lead]);

    svg.append("g")
        .call(d3.axisRight(y))
        .attr("transform", "translate(" + ((max_minute * x_scale * 60) + 5) + ", " + (margin.bottom + margin.top + yAxisShift) + ")")
        .append("text")
        .attr("fill", "#000")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end");

    var score_datas = [];
    var current_data = [];
    var current_score = 0;
    $.each(score_data, function() {
        if (this.score_margin === 0) {
            current_data.push(this);
        } else if ((current_score * this.score_margin) <= 0) {
            score_datas.push(current_data);
            current_data = [this];
            current_score = this.score_margin;
        } else {
            current_data.push(this);
            current_score = this.score_margin;
        }
    });
    score_datas.push(current_data);

    var line = d3.area()
        .x(function (d) {
            return x(d.minute);
        })
        .y0(function (d) {
            return y(0);
        })
        .y1(function (d) {
            return y(d.score_margin);
        })
        .curve(d3.curveStep);

    x.domain(d3.extent(score_data, function (d) {
        return +d.minute;
    }));


    $.each(score_datas, function () {
        var line_color = null;
        if (this[0].score_margin > 0){
            line_color = home_color;
        } else {
            line_color = away_color;
        }

        svg.append("path")
            .datum(this)
            .attr("class", "point-diff")
            .attr("fill", line_color)
            .attr("stroke", line_color)
            .attr("stroke-opacity", 1)
            .attr("stroke-linejoin", "bevel")
            .attr("stroke-linecap", "square")
            .attr("stroke-width", 3.5)
            .attr("opacity", 0.6)
            .attr("d", line)
            .attr("transform", "translate(" + -margin.left + "," + (margin.bottom + margin.top + yAxisShift) + ")");
    });

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

    if (max_minute > 48) {
        for (i = 0; i < ((max_minute - 48) / 5); i++) {
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

    svg.append("rect")
        .attr("x", 0)
        .attr("y", (top_team_player_count + bot_team_player_count + 3) * rect_height)
        .attr("rx", 1)
        .attr("ry", 1)
        .attr("class", "hour bordered")
        .attr("width", 300 * x_scale)
        .attr("height", rect_height - 5)
        .style("fill", 'black');

    svg.append("text")
        .attr("x", 310 * x_scale)
        .attr("y", (top_team_player_count + bot_team_player_count + 3.6) * rect_height)
        .text("Player On Court");

    svg.append("rect")
        .attr("x", 650 * x_scale)
        .attr("y", (top_team_player_count + bot_team_player_count + 3.5) * rect_height)
        .attr("rx", 1)
        .attr("ry", 1)
        .attr("width", 60 * x_scale)
        .attr("height", rect_height)
        .attr("opacity", 0.6)
        .style("fill", away_color);

    svg.append("text")
        .attr("x", 715 * x_scale)
        .attr("y", (top_team_player_count + bot_team_player_count + 4.2) * rect_height)
        .text(away_abb + " Lead");

    svg.append("rect")
        .attr("x", 650 * x_scale)
        .attr("y", (top_team_player_count + bot_team_player_count + 2.5) * rect_height)
        .attr("rx", 1)
        .attr("ry", 1)
        .attr("width", 60 * x_scale)
        .attr("height", rect_height)
        .attr("opacity", 0.6)
        .style("fill", home_color);

    svg.append("text")
        .attr("x", 715 * x_scale)
        .attr("y", (top_team_player_count + bot_team_player_count + 3.2) * rect_height)
        .text(home_abb + " Lead");
}
