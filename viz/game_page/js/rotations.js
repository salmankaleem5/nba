function plot_rotation_heat_map (rotation_data, score_data) {

  var margin = { top: 15, right: 150, bottom: 30, left: 170 },
      width = 1200 - margin.left - margin.right,
      height = 510 - margin.top - margin.bottom,
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

      if(this.minute > max_minute) {
        max_minute = this.minute;
      }
    });

    bot_team_player_count = (players.length - 1) - top_team_player_count;

    gridSize = Math.floor(width / max_minute) / 5;
    legendElementWidth = gridSize*2;

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
    minutes.push('end');

    var timeLabels = svg.selectAll(".timeLabel")
        .data(minutes)
        .enter().append("text")
          .text(function(d) { return d; })
          .attr("x", function(d, i) { return (i * gridSize); })
          .attr("y", (top_team_player_count + 1) * gridSize)
          .style("text-anchor", "middle")
          .attr("transform", "translate(" + (gridSize - 13) * 2 + ", -6)")
          .attr("class", "timeLabel mono axis axis-worktime");

    var playerColorScale = d3.scaleQuantile()
        .domain([0, 60])
        .range(playerColors);

    var cards = svg.selectAll(".hour")
        .data(rotation_data, function(d) {return d.pindex+':'+d.minute;});

    cards.append("title");

    cards.enter().append("rect")
        .attr("x", function(d) { return (d.minute - 1) * gridSize; })
        .attr("y", function(d) { return (d.pindex - 1) * gridSize; })
        .attr("rx", 4)
        .attr("ry", 4)
        .attr("class", "hour bordered")
        .attr("width", gridSize)
        .attr("height", gridSize)
        .style("fill", function(d) { return playerColorScale(d.value)});

    cards.select("title").text(function(d) { return d.value; });

    cards.exit().remove();

    var legend = svg.selectAll(".legend")
        .data([0].concat(playerColorScale.quantiles()), function(d) { return d; });

    var legend_y_shift = height - ((top_team_player_count + bot_team_player_count + 2) * gridSize);

    legend.enter().append("g")
        .attr("class", "legend")
        .append("rect")
        .attr("x", function(d, i) {return legendElementWidth * i; })
        .attr("y", height - legend_y_shift)
        .attr("width", legendElementWidth)
        .attr("height", gridSize)
        .style("fill", function(d, i) { return playerColors[i]; });

    legend.enter().append("text")
      .style("fill", function(d) { return playerColorScale(d < 30? 60 : 0);})
      .text(function(d, i) { return " ≥ " + Math.round(d); })
      .attr("x", function(d, i) { return legendElementWidth * i; })
      .attr("y", height + gridSize - legend_y_shift - 3)
      .attr("class", "legend");

    svg.selectAll(".legendLabel")
      .data(["Seconds Played in Minute"])
      .enter()
      .append("text")
      .text(function(d) {return d;})
      .attr("y", height + gridSize - (legend_y_shift + 3))
      .attr("x", function() { return (legend.enter().data().length * legendElementWidth) + 5})
      .attr("class", "legend");

    legend.exit().remove();

  var max_lead = 0;

  $.each(score_data, function(i, d) {
      if (Math.abs(this.score_margin) > max_lead) {
        max_lead = Math.abs(this.score_margin);
      }
  });
  var yAxisShiftBool = bot_team_player_count < top_team_player_count;

  var yAxisScale = (Math.min(top_team_player_count, bot_team_player_count) * 2 * gridSize);
      yAxisShift = yAxisShiftBool ? ((Math.abs(top_team_player_count - bot_team_player_count) - 0.8) * gridSize) : -27;

  console.log(max_lead);

  var x = d3.scaleLinear()
            .rangeRound([margin.left, width + margin.right + 70]);

  var y = d3.scaleLinear()
            .range([-margin.top, yAxisScale]);

  var line = d3.line()
                .x(function(d) { return x(d.minute); })
                .y(function(d) { return y(d.score_margin); })
                .curve(d3.curveStep);

  x.domain(d3.extent(score_data, function(d) { return +d.minute; }));
  y.domain([max_lead, -max_lead]);

  svg.append("g")
      .call(d3.axisRight(y))
      .attr("transform", "translate(" + (width + 60) + ", " + (margin.bottom + margin.top + yAxisShift) + ")")
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
      .attr("stroke-opacity", 0.7)
      .attr("stroke-linejoin", "bevel")
      .attr("stroke-linecap", "square")
      .attr("stroke-width", 3.5)
      .attr("d", line)
      .attr("transform", "translate(" + -margin.left + "," + (margin.bottom + margin.top + yAxisShift) + ")");;
}
