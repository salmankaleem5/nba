function plot_rotation_heat_map (rotation_data, score_data) {

  var margin = { top: 15, right: 150, bottom: 30, left: 350 },
      width = 1500 - margin.left - margin.right,
      height = 500 - margin.top - margin.bottom,
      gridSize = 0,
      legendElementWidth = 0,
      buckets = 9,
      playerColors = colorbrewer.Greys[9],
      max_minute = 0,
      top_team_player_count = 0,
      bot_team_player_count = 0,
      max_pindex = 0;

  var svg = d3.select("#chart").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    rotation_data.sort(function(a,b) {
      if (a.pindex == b.pindex)
        return 0;
      if (a.pindex < b.pindex)
        return -1;
      if (a.pindex > b.pindex)
        return 1;
    });

    var players = [],
        previous_pindex = 0;

    $.each(rotation_data, function(i, d) {
      if ($.inArray(this.player, players) === -1) {
        if (this.pindex - previous_pindex > 1) {
          players.push("");
          top_team_player_count=this.pindex-2;
        }
        players.push(this.player);
      }
      previous_pindex = this.pindex;

      if(this.pindex > max_pindex) {
        max_pindex = this.pindex;
      }

      if(+this.end_time > max_minute) {
        max_minute = +this.end_time;
      }
    });

    max_minute = max_minute / 60;

    bot_team_player_count = (players.length - 1) - top_team_player_count;

    gridSize = Math.floor(height / (max_pindex + 2));
    legendElementWidth = gridSize*2;

    var x_scale = (width - margin.right) / (max_minute * 60);

    var playerLabels = svg.selectAll(".playerLabel")
        .data(players)
        .enter().append("text")
          .text(function (d) { return d; })
          .attr("x", 0)
          .attr("y", function (d, i) { return (i * gridSize); })
          .style("text-anchor", "end")
          .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
          .attr("class", "dayLabel axis axis-workweek");

    var minutes = ["Q1","","","","","","","","","","","","Q2","","","","","","","","","","","","Q3","","","","","","","","","","","","Q4","","","","","","","","","",""];
    if (max_minute >= 48) {
      extra_minutes = max_minute - 48;
      for (i = 0; i < extra_minutes; i++) {
        if(i % 5 == 0) {
          minutes.push("OT" + (i/5 + 1));
        }
        else {
          minutes.push("");
        }
      };
    }
    minutes.push('E');

    var timeLabels = svg.selectAll(".timeLabel")
        .data(minutes)
        .enter().append("text")
          .text(function(d) { return d; })
          .attr("x", function(d, i) { return (i * 60 * x_scale); })
          .attr("y", (top_team_player_count + 1) * gridSize)
          .style("text-anchor", "middle")
          .attr("transform", "translate(" + (gridSize/2) + ", -6)")
          .attr("class", "timeLabel mono axis axis-worktime");

    var playerColorScale = d3.scaleQuantile()
        .domain([0, 60])
        .range(playerColors);

    var cards = svg.selectAll(".hour")
        .data(rotation_data, function(d) {return d.pindex+':'+d.minute;});

    cards.append("title");

    cards.enter().append("rect")
        .attr("x", function(d) { return d.start_time * x_scale; })
        .attr("y", function(d) { return (d.pindex - 1) * gridSize; })
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("class", "hour bordered")
        .attr("width", function(d) {return (d.end_time - d.start_time) * x_scale;})
        .attr("height", gridSize - 2)
        .style("fill", 'black');

    cards.select("title").text(function(d) { return d.value; });

    cards.exit().remove();

  var max_lead = 0;

  $.each(score_data, function(i, d) {
      if (Math.abs(this.score_margin) > max_lead) {
        max_lead = Math.abs(this.score_margin);
      }
  });
  var yAxisShiftBool = bot_team_player_count < top_team_player_count;

  var yAxisScale = (((Math.min(top_team_player_count, bot_team_player_count) * 2) + 1) * gridSize) + 15;
      yAxisShift = yAxisShiftBool ? ((Math.abs(top_team_player_count - bot_team_player_count)) * gridSize) - margin.top - 17 : -margin.bottom;

  var x = d3.scaleLinear()
            .rangeRound([margin.left, width + margin.left - margin.right]);

  var y = d3.scaleLinear()
            .range([-margin.top, yAxisScale - margin.bottom]);

  var line = d3.line()
                .x(function(d) { return x(d.minute); })
                .y(function(d) { return y(d.score_margin); })
                .curve(d3.curveStep);

  x.domain(d3.extent(score_data, function(d) { return +d.minute; }));
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

  svg.append("line")
      .attr("x1", 0)
      .attr("x2", 0)
      .attr("y1", 0)
      .attr("y2", gridSize * (max_pindex + 1))
      .style("stroke-width", 2)
      .attr("stroke-opacity", 0.2)
      .style("stroke", 'black')
      .style("fill", 'none');

  svg.append("line")
      .attr("x1", 720 * x_scale)
      .attr("x2", 720 * x_scale)
      .attr("y1", 0)
      .attr("y2", gridSize * (max_pindex + 1))
      .style("stroke-width", 2)
      .attr("stroke-opacity", 0.2)
      .style("stroke", 'black')
      .style("fill", 'none');

  svg.append("line")
      .attr("x1", 1440 * x_scale)
      .attr("x2", 1440 * x_scale)
      .attr("y1", 0)
      .attr("y2", gridSize * (max_pindex + 1))
      .style("stroke-width", 2)
      .attr("stroke-opacity", 0.2)
      .style("stroke", 'black')
      .style("fill", 'none');

  svg.append("line")
      .attr("x1", 2160 * x_scale)
      .attr("x2", 2160 * x_scale)
      .attr("y1", 0)
      .attr("y2", gridSize * (max_pindex + 1))
      .style("stroke-width", 2)
      .attr("stroke-opacity", 0.2)
      .style("stroke", 'black')
      .style("fill", 'none');
}
