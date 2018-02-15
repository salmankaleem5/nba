function plot_rotations(){
  var margin = { top: 15, right: 150, bottom: 0, left: 170 },
      width = 1200 - margin.left - margin.right,
      height = 500 - margin.top - margin.bottom,
      gridSize = Math.floor(width / 47),
      legendElementWidth = gridSize*2,
      buckets = 9,
      playerColors = colorbrewer.Greys[9],
      max_minute = 0,
      top_team_player_count = 0,
      max_pindex = 0;

  var svg = d3.select("#chart").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var heatmapChart = function(csvFile) {
    d3.csv(csvFile,
    function(d) {
      return {
        player: d.player,
        minute: +d.minute,
        value: +d.value,
        pindex: +d.pindex
      };
    },
    function(error, data) {

      data.sort(function(a,b) {
        if (a.pindex == b.pindex)
          return 0;
        if (a.pindex < b.pindex)
          return -1;
        if (a.pindex > b.pindex)
          return 1;
      });

      var players = [],
          previous_pindex = 0;

      $.each(data, function(i, d) {
        if ($.inArray(this.player, players) === -1) {
          if (this.pindex - previous_pindex > 1) {
            players.push("");
            top_team_player_count=this.pindex-1;
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

      var playerLabels = svg.selectAll(".playerLabel")
          .data(players)
          .enter().append("text")
            .text(function (d) { return d; })
            .attr("x", 0)
            .attr("y", function (d, i) { return (i * gridSize); })
            .style("text-anchor", "end")
            .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
            .attr("class", "dayLabel axis axis-workweek");

      minutes = ["Q1","","","","","","","","","","","","Q2","","","","","","","","","","","","Q3","","","","","","","","","","","","Q4","","","","","","","","","",""];
      if (max_minute >= 48) {
        extra_minutes = max_minute - 48;
        for (i = 0; i < extra_minutes; i++) {
          if(i % 5 == 0) {
            minutes.push("OT" + ((i + 1) - (5 * i)));
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
            .attr("x", function(d, i) { return (i * gridSize) -5; })
            .attr("y", top_team_player_count * gridSize)
            .style("text-anchor", "middle")
            .attr("transform", "translate(" + (gridSize - 13) * 2 + ", -6)")
            .attr("class", "timeLabel mono axis axis-worktime");

      var playerColorScale = d3.scaleQuantile()
          .domain([0, 60])
          .range(playerColors);

      var cards = svg.selectAll(".hour")
          .data(data, function(d) {return d.pindex+':'+d.minute;});

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
    });
  };

  var lineChart = function(csvFile) {
    d3.csv(csvFile,
      function(d) {
        return {
          minute: +d.minute,
          score_margin: +d.score_margin
        };
      }, function(error, data){
        var max_home_lead = 0,
            max_vis_lead = 0;

        $.each(data, function(i, d) {
            if (this.score_margin > max_home_lead) {
              max_home_lead = this.score_margin;
            }
            if (this.score_margin < max_vis_lead) {
              max_vis_lead = this.score_margin;
            }
        });
        max_vis_lead = Math.abs(max_vis_lead);

        var max_lead_diff = max_home_lead - max_vis_lead,
            max_lead = Math.max(max_home_lead, max_vis_lead),
            max_lead_ratio = Math.min(max_home_lead, max_vis_lead) / Math.max(max_home_lead, max_vis_lead);

        var yAxisShiftBool = max_lead_ratio == max_home_lead ? true : false;

        var yAxisScale = height - (((max_pindex * gridSize) / 2) * (1 + max_lead_ratio)),
            yAxisShift = yAxisShiftBool ? (1 - max_lead_ratio) * (height / 2) : 0;

        console.log(yAxisShift);

        var x = d3.scaleLinear()
          .rangeRound([margin.left, width + margin.right]);

        var y = d3.scaleLinear()
          .rangeRound([height - margin.top, yAxisScale]);

        var line = d3.line()
          .x(function(d) { return x(d.minute); })
          .y(function(d) { return y(d.score_margin); })
          .curve(d3.curveStep);

        x.domain(d3.extent(data, function(d) { return +d.minute; }));
        y.domain(d3.extent(data, function(d) { return +d.score_margin; }));

        svg.append("g")
          .call(d3.axisRight(y))
          .attr("transform", "translate(" + width + ", " + (margin.bottom - yAxisScale + yAxisShift) + ")")
          .append("text")
          .attr("fill", "#000")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", "0.71em")
          .attr("text-anchor", "end")

        svg.append("path")
          .datum(data)
          .attr("fill", "none")
          .attr("stroke", "steelblue")
          .attr("stroke-opacity", 0.7)
          .attr("stroke-linejoin", "bevel")
          .attr("stroke-linecap", "square")
          .attr("stroke-width", 3.5)
          .attr("d", line)
          .attr("transform", "translate(" + -margin.left + "," + (margin.bottom - yAxisScale + yAxisShift) + ")");;
      })
  };
  heatmapChart("./data/data.csv");
  lineChart("./data/score.csv");
}
