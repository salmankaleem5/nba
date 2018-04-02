$(document).ready(function() {

  var player_data = null;

  $.getJSON("./data/shots.json", function(json) {
    console.log(json);
    let shot_totals = {},
      players = Object.keys(json['players']);

    const player_select = $('#player-select');

    player_select.append($('<option></option>').val('').html(''));
    $.each(players, function(i, p) {
      player_select.append($('<option></option>').val(p).html(p));
    });

    //player_select.selectpicker({});

    const courtSelection = d3.select("#shot-chart");

    let svg = d3.select("svg");

    const width = 1000,
      yScale = d3.scaleLinear().domain([0, 47]).rangeRound([47, 0]),
      colors = ["#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7", "#f7f7f7", "#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061"].reverse(),
      pctHeatScale = d3.scaleQuantize().domain([-0.1, 0.1]).range(colors),
      efgHeatScale = d3.scaleQuantize().domain([-0.15, 0.15]).range(colors);

    courtSelection.style("max-width", width / 16 + "em");
    courtSelection.style("margin", "auto");

    //region court draw
    svg = courtSelection.append("svg")
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
    let restrictedArea = svg.append("g").classed("restricted-area", true);
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

    //endregion

    //region legend

    svg.append("g").classed("legend", true);
    let legendGroup = svg.select(".legend");

    let eff_legend = legendGroup.selectAll('.effLegendElement')
      .data(colors, function(d) {
        return d;
      });

    eff_legend.enter().append("rect")
      .attr("x", function(d, i) {
        return i + 1;
      })
      .attr("y", yScale(-1))
      .attr("width", 1)
      .attr("height", 1)
      .attr("rx", 0.2)
      .attr("ry", 0.2)
      .style("fill", function(d, i) {
        return colors[i]
      });

    let eff_legend_text = ["Less Efficient", "", "", "", "", "", "", "More Efficient"];
    let effLegendText = legendGroup.selectAll('.effLegendElement')
      .data(eff_legend_text, function(d) {
        return d;
      });

    effLegendText.enter().append("text")
      .attr("x", function(d, i) {
        return i * 0.9 + 1;
      })
      .attr("y", yScale(-3))
      .text(function(d, i) {
        return eff_legend_text[i]
      })
      .attr("fill", "white");

    sizes = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    let vol_legend = legendGroup.selectAll(".volLegendElement")
      .data(sizes, function(d) {
        return d;
      });

    let x_shift = 0;
    vol_legend.enter().append("rect")
      .attr("x", function(d, i) {
        x_shift += d + 0.3;
        return x_shift - d + 40;
      })
      .attr("y", function(d, i) {
        return yScale(-1) + (1-d)/2;
      })
      .attr("width", function(d, i) {
        return d;
      })
      .attr("height", function(d, i) {
        return d;
      })
      .attr("rx", 0.2)
      .attr("ry", 0.2)
      .style("fill", "white")

    let vol_legend_text = ["Fewer Shots", "", "", "", "", "", "More Shots"];
    let volLegendText = legendGroup.selectAll('.volLegendElement')
      .data(vol_legend_text, function(d) {
        return d;
      });

    effLegendText.enter().append("text")
      .attr("x", function(d, i) {
        return i * 0.9 + 40;
      })
      .attr("y", yScale(-3))
      .text(function(d, i) {
        return vol_legend_text[i]
      })
      .attr("fill", "white");

    //endregion

    player_select.change(function() {
      let player = $('#player-select option:selected').val();
      player_data = json['players'][player];

      let shotsGroup = svg.select(".shots");

      let shots = shotsGroup.selectAll(".shot")
        .data([], function(d) {
          return [];
        });

      shots.exit()
        .transition().duration(1000)
        .attr("height", 0)
        .attr("width", 0)
        .remove();

      shots = shotsGroup.selectAll(".shot")
        .data(player_data['xy'], function(d) {
          return [d.x, d.y, d.attempts];
        });

      shots.enter()
        .append("rect")
        .classed("shot", true)
        .attr("x", function(d) {
          size = Math.min(1, d.attempts / 5);
          return 50 - (d.x + 25 + size/2);
        })
        .attr("y", function(d) {
          size = Math.min(1, d.attempts / 5)
          return yScale(d.y) - 5 - size/2;
        })
        .transition().duration(1000)
        .attr("width", function(d) {
          return Math.min(1, d.attempts / 5);
        })
        .attr("height", function(d) {
          return Math.min(1, d.attempts / 5);
        })
        .attr("rx", 0.2)
        .attr("ry", 0.2)
        .style("fill", function(d) {
          if (eff_toggle[0].checked) {
            return efgHeatScale(player_data['zones'][json['zone_map'][d.x][d.y]]['overall_rel_efg']);
          } else {
            return pctHeatScale(player_data['zones'][json['zone_map'][d.x][d.y]]['zone_rel_pct']);
          }
        });
    });

    var eff_toggle = $("#eff-change");

    eff_toggle.click(function() {
      let shotsGroup = svg.select(".shots");
      let shots = shotsGroup.selectAll(".shot");

      if (this.checked) {
        shots
          .transition().duration(1000)
          .style("fill", function(d) {
            return efgHeatScale(player_data['zones'][json['zone_map'][d.x][d.y]]['overall_rel_efg']);
          });
      } else {
        shots
          .transition().duration(1000)
          .style("fill", function(d) {
            return pctHeatScale(player_data['zones'][json['zone_map'][d.x][d.y]]['zone_rel_pct']);
          });
      }
    });

  });

});
