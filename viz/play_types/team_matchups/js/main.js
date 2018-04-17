function update_colors(offensive_team, defensive_team) {
    d3.selectAll(".player")
        .transition().duration(1000)
        .attr("r", function (d) {
            if (((d.Team === offensive_team) && (d.Side === "offensive")) || ((d.Team === defensive_team) && (d.Side === "defensive"))) {
                return 5;
            }
            else {
                return 3.5;
            }
        })
        .attr("opacity", function (d) {
            if (((d.Team === offensive_team) && (d.Side === "offensive")) || ((d.Team === defensive_team) && (d.Side === "defensive"))) {
                return 1;
            } else {
                return 0.3;
            }
        })
        .style("fill", function (d) {
            if ((d.Team === offensive_team) && (d.Side === "offensive")) {
                return "blue";
            } else if ((d.Team === defensive_team) && (d.Side === "defensive")) {
                return "red";
            } else {
                return "grey";
            }
        });
}


$(document).ready(function () {

    let offensive_team, defensive_team;

    $.getJSON('./data/data.json')
        .success(function (data) {

            const play_types = Object.keys(data);

            let team_list = [];

            const margin = {top: 0, right: 0, bottom: 0, left: 0},
                width = $(window).width() - margin.left - margin.right - 20,
                height = $(window).height() - margin.top - margin.bottom - 100;

            let svg = d3.select("#chart").append("svg")
                .attr("width", width)
                .attr("height", height);

            console.log(width);
            console.log(height);

            svg.append("text")
                .attr("x", 0)
                .attr("y", 0)
                .attr("transform", "translate(10," + ((height / 2) + 50) + ") rotate(-90)")
                .text("Points Per Possession");

            svg.append("text")
                .attr("x", (width / 2) - 50)
                .attr("y", height - 3)
                .text("Possessions Per Game");

            $.each(play_types, function (ix, pt) {
                let pt_data = data[pt];

                // let new_teams = pt_data.map(a => a.Team).filter(function (d) {
                //     return $.inArray(d, team_list) === -1;
                // });
                //
                // team_list.push.apply(team_list, new_teams);

                if (ix === 0) {
                    team_list = pt_data.filter(function (d) {
                        return d.Side === "offensive"
                    }).map(a => a.Team)
                }

                let startPos = {"x": (ix % 5) * (width / 5) + 20, "y": ix < 5 ? 10 : height / 2};

                const maxPPP = d3.max(pt_data, function (d) {
                        return d.PPP;
                    }),
                    minPPP = d3.min(pt_data, function (d) {
                        return d.PPP;
                    }),
                    maxTime = d3.max(pt_data, function (d) {
                        return d.PossG;
                    });

                svg.append("text")
                    .attr("x", startPos.x + (width / 10))
                    .attr("y", startPos.y + 30)
                    .attr("text-anchor", "middle")
                    .text(pt);

                const x = d3.scaleLinear().rangeRound([10, (width / 5) - 70]);
                const y = d3.scaleLinear().rangeRound([50, (height / 2) - 70]);

                x.domain([0, maxTime]);
                y.domain([maxPPP, minPPP]);

                svg.append("g")
                    .call(d3.axisRight(y).ticks(4).tickSize(0))
                    .attr("transform", "translate(" + startPos.x + "," + startPos.y + ")")
                    .append("text");

                svg.append("g")
                    .call(d3.axisBottom(x).ticks(4).tickSize(0))
                    .attr("transform", "translate(" + startPos.x + "," + (startPos.y + height / 2 - 30) + ")")
                    .append("text");


                svg.selectAll(".player")
                    .data(pt_data, function (d) {
                        return [d.Team, d.Side, d.PossG, d.PPP];
                    }).enter()
                    .append("circle")
                    .classed("player", true)
                    .attr("cx", function (d) {
                        return startPos.x + x(d.PossG);
                    })
                    .attr("cy", function (d) {
                        return startPos.y + y(d.PPP);
                    })
                    .attr("r", 3.5)
                    .attr("opacity", 0.3)
                    .style("fill", "grey");
            });

            team_list.sort();

            let offense_select = $("#offense-select"),
                defense_select = $("#defense-select");

            offense_select.append(($('<option></option>').val('').html('')));
            defense_select.append(($('<option></option>').val('').html('')));
            $.each(team_list, function (i, d) {
                offense_select.append(($('<option></option>').val(d).html(d)));
                defense_select.append(($('<option></option>').val(d).html(d)));
            });

            offense_select.change(function () {
                offensive_team = this.value;
                update_colors(offensive_team, defensive_team);
            });

            defense_select.change(function () {
                defensive_team = this.value;
                update_colors(offensive_team, defensive_team);
            })

                .error(function (error, msg) {
                    console.log(error);
                    console.log(msg);
                });
        });
});
