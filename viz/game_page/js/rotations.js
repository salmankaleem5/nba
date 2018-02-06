function plot_rotations(){
  var margin = { top: 15, right: 60, bottom: 0, left: 150 },
      width = 960 - margin.left - margin.right,
      height = 360 - margin.top - margin.bottom,
      gridSize = Math.floor(width / 47),
      legendElementWidth = gridSize*2,
      buckets = 9,
      playerColors = colorbrewer.Greens[9],
      minutes = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44","45","46","47","48",],
      players = ["Andrew Wiggins","Jimmy Butler","Taj Gibson","Karl-Anthony Towns","Jeff Teague","Jamal Crawford","Tyus Jones","Gorgui Dieng","Nemanja Bjelica","Marcus Georges-Hunt","Aaron Brooks","", "Jrue Holiday","Anthony Davis","Nikola Mirotic","Ian Clark","Darius Miller","Rajon Rondo","Dante Cunningham","Cheick Diallo","E'Twaun Moore","Mike James","Charles Cooke"];

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
        .attr("class", "dayLabel mono axis axis-workweek");

  var timeLabels = svg.selectAll(".timeLabel")
      .data(minutes)
      .enter().append("text")
        .text(function(d) { return d; })
        .attr("x", function(d, i) { return (i * gridSize) + 3; })
        .attr("y", 168)
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
          .domain([0, 1])
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

  var yAxisScale = 165;

  var x = d3.scaleLinear()
    .rangeRound([margin.left, width + 110]);

  var y = d3.scaleLinear()
    .rangeRound([height - margin.top, margin.bottom + yAxisScale]);

  var line = d3.line()
    .x(function(d) { return x(d.minute); })
    .y(function(d) { return y(d.score_margin); });

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
          .attr("transform", "translate(725, " + (margin.bottom - yAxisScale) + ")")
          .append("text")
          .attr("fill", "#000")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", "0.71em")
          .attr("text-anchor", "end")

        svg.append("path")
          .datum(data)
          .attr("fill", "none")
          .attr("style", "z-index")
          .attr("stroke", "steelblue")
          .attr("stroke-linejoin", "round")
          .attr("stroke-linecap", "round")
          .attr("stroke-width", 3.5)
          .attr("d", line)
          .attr("transform", "translate(" + -150 + "," + (margin.bottom - yAxisScale) + ")");;
      })
  };
  heatmapChart("./data/data.csv");
  lineChart("./data/score.csv");
}
