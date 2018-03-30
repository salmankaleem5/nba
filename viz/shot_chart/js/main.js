$(document).ready(function () {


    $.getJSON("./data/shots.json", function (json) {
        let x = {},
            players = [''];

        $.each(json, function (i, d) {
            if ($.inArray(this.player, players) === -1) {
                players.push(this.player);
                x[this.player] = 1;
            }
            else {
                x[this.player]++;
            }
        });
        players.sort(function (a, b) {
            return x[b] - x[a];
        });

        let player_select = $('#player-select');

        $.each(players, function (i, p) {
            player_select.append($('<option></option>').val(p).html(p));
        });

        //player_select.selectpicker({});

        var courtSelection = d3.select("#shot-chart");

        var svg = d3.select("svg");

        let width = 1000,
            height = .94 * width,
            yScale = d3.scaleLinear().domain([0, 47]).rangeRound([47, 0]),
            yScale$1 = d3.scaleLinear().domain([0, 47]).rangeRound([47, 0]);

        courtSelection.style("max-width", width / 16 + "em");
        courtSelection.style("margin", "auto");

        let all_zones = {};

        $.each(json, function (i, d) {
            if ((d.zone + '-' + d.area) in all_zones) {
                all_zones[d.zone + '-' + d.area]['attempts'] += 1;
                all_zones[d.zone + '-' + d.area]['makes'] += d.shot_made_flag;
            } else {
                all_zones[d.zone + '-' + d.area] = {};
                all_zones[d.zone + '-' + d.area]['attempts'] = 1;
                all_zones[d.zone + '-' + d.area]['makes'] = d.shot_made_flag;
                all_zones[d.zone + '-' + d.area]['val'] = d.shot_type === '3PT Field Goal' ? 3 : 2;
            }
        });

        let total_points = 0,
            total_attempts = 0;

        $.each(all_zones, function (i, z) {
            let pct = z['makes'] / z['attempts'];
            z['pct'] = pct;
            z['eff'] = pct * z['val'];

            total_points += z['val'] * z['makes'];
            total_attempts += z['attempts'];
        });

        let total_avg_eff = total_points / total_attempts,
            colors = ["#67001f","#b2182b","#d6604d","#f4a582","#fddbc7","#f7f7f7","#d1e5f0","#92c5de","#4393c3","#2166ac","#053061"].reverse(),
            totalAvgHeatScale = d3.scaleQuantize().domain([total_avg_eff - 0.2, total_avg_eff + 0.2]).range(colors),
            byZoneHeatScale = d3.scaleQuantize().domain([-0.2, 0.2]).range(colors);

        console.log(total_avg_eff);

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

        svg.append("g").classed("legend", true);
        let legendGroup = svg.select(".legend");

        let legend = legendGroup.selectAll('.legendElement')
            .data(colors, function (d) { return d; });

        legend.enter().append("rect")
            .attr("x", function (d, i) { return i*1.5 + 1; })
            .attr("y", yScale(-1))
            .attr("width", 1.5)
            .attr("height",1.5)
            .attr("rx", 0.2)
            .attr("ry", 0.2)
            .style("fill", function (d, i) { return colors[i]});

        let legend_text = ["Less Efficient", "", "","","","", "", "", "More Efficient"];
        let legendText = legendGroup.selectAll('.legendElement')
            .data(legend_text, function (d) {return d; });

        legendText.enter().append("text")
            .attr("x", function (d, i) { return i*1.5 + 1.2; })
            .attr("y", yScale(-2))
            .text(function (d, i) { return legend_text[i]});


        player_select.change(function () {
            let player = $('#player-select option:selected').val(),
                player_data = json.filter(function (d) {
                    return d.player === player;
                });

            let xs = [],
                ys = [],
                player_zones = {};

            $.each(player_data, function (i, d) {
                let x = Math.round(d.x),
                    y = Math.round(d.y);

                if (!xs.includes(x)) {
                    xs.push(x);
                }
                if (!ys.includes(y)) {
                    ys.push(y);
                }
                if ((d.zone + '-' + d.area) in player_zones) {
                    player_zones[d.zone + '-' + d.area]['attempts'] += 1;
                    player_zones[d.zone + '-' + d.area]['makes'] += d.shot_made_flag;
                } else {
                    player_zones[d.zone + '-' + d.area] = {};
                    player_zones[d.zone + '-' + d.area]['attempts'] = 1;
                    player_zones[d.zone + '-' + d.area]['makes'] = d.shot_made_flag;
                    player_zones[d.zone + '-' + d.area]['val'] = d.shot_type === '3PT Field Goal' ? 3 : 2;
                }
            });

            $.each(player_zones, function (i, z) {
                let pct = z['makes'] / z['attempts'];
                z['pct'] = pct;
                z['eff'] = pct * z['val'];
            });

            console.log(all_zones);
            console.log(player_zones);

            let nestedData = [];
            $.each(xs, function (i, q) {
                $.each(ys, function (j, w) {
                    let this_data = player_data.filter(function (td) {
                        return (Math.round(td.x) === q) & (Math.round(td.y) === w);
                    });
                    if (this_data.length > 0) {
                        nestedData.push({
                            'x': q,
                            'y': w,
                            'attempts': this_data.length,
                            'makes': d3.sum(this_data, function (td) {
                                return td.shot_made_flag;
                            }),
                            'pct': d3.sum(this_data, function (td) {
                                return td.shot_made_flag;
                            }) / this_data.length,
                            'eff': (d3.sum(this_data, function (td) {
                                return td.shot_made_flag;
                            }) / this_data.length) * (this_data[0].shot_type === '3PT Field Goal' ? 3 : 2),
                            'zone': this_data[0].zone + '-' + this_data[0].area,
                            'zone_eff': player_zones[this_data[0].zone + '-' + this_data[0].area]['eff'],
                            'player': player_data[0].shooter
                        });
                    }
                });
            });

            let shotsGroup = svg.select(".shots");

            let shots = shotsGroup.selectAll(".shot")
                .data(nestedData, function (d) {
                    return [d.player, d.x, d.y, d.attempts, d.pct]
                });

            shots.exit()
                .transition().duration(1000)
                .attr("height", 0)
                .attr("width", 0)
                .remove();

            shots.enter()
                .append("rect")
                .classed("shot", true)
                .attr("x", function (d) {
                    return 50 - (d.x + 25);
                })
                .attr("y", function (d) {
                    return yScale$1(d.y) - 5;
                })
                .transition().duration(1000)
                .attr("width", function (d) {
                    return Math.min(1, d.attempts / 7);
                })
                .attr("height", function (d) {
                    return Math.min(1, d.attempts / 7);
                })
                .attr("rx", 0.2)
                .attr("ry", 0.2)
                .style("fill", function (d) {
                    return totalAvgHeatScale(d.zone_eff);
                });
        });

        $("#eff-change").click(function () {
            let shotsGroup = svg.select(".shots");
            let shots = shotsGroup.selectAll(".shot");

            shots
                .transition().duration(1000)
                .style("fill", function (d) {
                return byZoneHeatScale(d.zone_eff - all_zones[d.zone]['eff'])
            });
        });

    });

});

