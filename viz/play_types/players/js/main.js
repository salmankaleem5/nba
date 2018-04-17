function is_in_selected_players(d, selected_players) {
    $.each(selected_players, function (ix, p) {
        if ((d.Player === p.name) && (d.Year === p.year)) {
            return true
        }
    });
    return false;
}


function change_player(selected_players) {
    d3.selectAll(".player")
        .transition().duration(1000)
        .attr("r", function (d) {
            if (is_in_selected_players(d, selected_players)) {
                return 5;
            } else {
                return 3.5;
            }
        })
        .attr("opacity", function (d) {
            if (is_in_selected_players(d, selected_players)) {
                return 1;
            } else {
                return 0.3;
            }
        })
        .style("fill", function (d) {
            if (is_in_selected_players(d, selected_players)) {
                return "blue";
            } else {
                return "grey";
            }
        })
}


$(document).ready(function () {

    let selected_players = [];

    $.getJSON('./data/data.json')
        .success(function (data) {

            const play_types = Object.keys(data);

            let player_list = [];

            const margin = {top: 0, right: 0, bottom: 0, left: 0},
                width = $(window).width() - margin.left - margin.right - 20,
                height = $(window).height() - margin.top - margin.bottom - 20;

            let svg = d3.select("#chart").append("svg")
                .attr("width", width)
                .attr("height", height);

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

                let new_players = pt_data.map(a => a.Player).filter(function (d) {
                    return $.inArray(d, player_list) === -1;
                });

                $.each(new_players, function(jx, p) {
                    if ($.inArray(p, player_list) === -1) {
                        player_list.push(p)
                    }
                });

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
                        return [d.Player, d.PossG, d.PPP, d.Year];
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

            player_list.sort();

            let player_select = $("#player-select"),
                year_select = $("#year-select"),
                add_player = $("#player-add");

            player_select.append(($('<option></option>').val('').html('')));
            $.each(player_list, function (i, d) {
                player_select.append(($('<option></option>').val(d).html(d)));
            });

            add_player.click(function () {
                let player = {
                    'name': player_select.val(),
                    'year': year_select.val()
                };
                selected_players.push(player);
                change_player(selected_players);
            })

        })

        .error(function (error, msg) {
            console.log(error);
            console.log(msg);
        });

});
