function plot_rotations(){
  var margin = { top: 15, right: 150, bottom: 0, left: 150 },
      width = 1200 - margin.left - margin.right,
      height = 500 - margin.top - margin.bottom,
      gridSize = Math.floor(width / 47),
      legendElementWidth = gridSize*2,
      buckets = 9,
      playerColors = colorbrewer.Greys[9],
      minutes = ["Q1","","","","","","","","","","","","Q2","","","","","","","","","","","","Q3","","","","","","","","","","","","Q4","","","","","","","","","","","","OT1", "", "", "", "end"],
      players = ["LeBron James","JR Smith","Isaiah Thomas","Jeff Green","Tristan Thompson","Jae Crowder","Cedi Osman","Channing Frye","Kyle Korver","Derrick Rose","", "Jimmy Butler","Andrew Wiggins","Jeff Teague","Karl-Anthony Towns","Taj Gibson","Jamal Crawford","Nemanja Bjelica","Gorgui Dieng","Tyus Jones"];

  var svg = d3.select("#chart").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var dayLabels = svg.selectAll(".dayLabel")
      .data(players)
      .enter().append("text")
        .text(function (d) { return d; })
        .attr("x", 0)
        .attr("y", function (d, i) { return (i * gridSize); })
        .style("text-anchor", "end")
        .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
        .attr("class", "dayLabel axis axis-workweek");

  var timeLabels = svg.selectAll(".timeLabel")
      .data(minutes)
      .enter().append("text")
        .text(function(d) { return d; })
        .attr("x", function(d, i) { return (i * gridSize) -5; })
        .attr("y", 210)
        .style("text-anchor", "middle")
        .attr("transform", "translate(" + (gridSize - 13) * 2 + ", -6)")
        .attr("class", "timeLabel mono axis axis-worktime");

  var heatmapChart = function(csvFile) {
    d3.csv(csvFile,
    function(d) {
      return {
        day: +d.player,
        hour: +d.minute,
        value: +d.value,
        pindex: +d.pindex
      };
    },
    function(error, data) {
      var playerColorScale = d3.scaleQuantile()
          .domain([0, 60])
          .range(playerColors);

      var cards = svg.selectAll(".hour")
          .data(data, function(d) {return d.pindex+':'+d.hour;});

      cards.append("title");

      cards.enter().append("rect")
          .attr("x", function(d) { return (d.hour - 1) * gridSize; })
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

  var yAxisShift = 170;
  var xAxisShift = 260;

  var x = d3.scaleLinear()
    .rangeRound([margin.left, width + xAxisShift]);

  var y = d3.scaleLinear()
    .rangeRound([height - margin.top, margin.bottom + yAxisShift]);

  var line = d3.line()
    .x(function(d) { return x(d.minute); })
    .y(function(d) { return y(d.score_margin); })
    .curve(d3.curveStep);

  var lineChart = function(csvFile) {
    d3.csv(csvFile,
      function(d) {
        return {
          minute: +d.minute,
          score_margin: +d.score_margin
        };
      }, function(error, data){
        x.domain(d3.extent(data, function(d) { return +d.minute; }));
        y.domain(d3.extent(data, function(d) { return +d.score_margin; }));

        svg.append("g")
          .call(d3.axisRight(y))
          .attr("transform", "translate(1010, " + (margin.bottom - yAxisShift) + ")")
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
          .attr("transform", "translate(" + -150 + "," + (margin.bottom - yAxisShift) + ")");;
      })
  };
  heatmapChart("./data/data.csv");
  lineChart("./data/score.csv");
}
