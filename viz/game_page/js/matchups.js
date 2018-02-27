function plot_matchups(json) {
  var height = 300,
      width = 300,
      radius = Math.min(width, height) / 2;

  var svg = d3.select("#match-ups").append("svg")
              .attr("width", width)
              .attr("height", height);

  var g = svg.append("g")
              .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

  var color = colorbrewer.Set1[9];

  var pie = d3.pie()
              .sort(null)
              .value(function(d) { return d.POSS; });

  var path = d3.arc()
                .outerRadius(radius - 10)
                .innerRadius(0);

  var label = d3.arc()
                .outerRadius(radius - 60)
                .innerRadius(radius - 60);

  var arc = g.selectAll(".arc")
              .data(pie(json))
              .enter().append("g")
                      .attr("class", "arc");

  var i=0;

  arc.append("path")
      .attr("d", path)
      .attr("fill", function(d) { return color[i++]; });

  arc.append("text")
      .attr("transform", function(d) { console.log(label.centroid(d)); return "translate(" + label.centroid(d) + ")"; })
      .attr("dy", "0.35em")
      .html(function(d) { return d.data.DEF_PLAYER_NAME.split(' ')[1]; });
}
