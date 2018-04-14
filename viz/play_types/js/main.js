$(document).ready(function () {

    $.getJSON('./data/data.json')
        .success(function (data) {

            const play_types = Object.keys(data);

            let player_list = [];

            $.each(play_types, function (ix, pt) {
                let pt_data = data[pt];

                let new_players = pt_data.map(a => a.Player).filter(function (d) {return $.inArray(d, player_list) === -1;});
                player_list.push.apply(player_list, new_players);

                const margin = {top: 0, right: 0, bottom: 0, left: 0},
                    width = ($(window).width() / 5.5) - margin.left - margin.right,
                    height = ($(window).height() / 2.5) - margin.top - margin.bottom;

                const maxPPP = d3.max(pt_data, function (d) {
                        return d.PPP;
                    }),
                    minPPP = d3.min(pt_data, function (d) {
                        return d.PPP;
                    }),
                    maxTime = d3.max(pt_data, function (d) {
                        return d.PossG;
                    });

                let svg = d3.select("#chart").append("svg")
                    .attr("width", width)
                    .attr("height", height)
                    .attr("transform", "translate(0,0)")
                    .style("padding", "10px");

                svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", 15)
                    .attr("text-anchor", "middle")
                    .text(pt);

                const x = d3.scaleLinear().rangeRound([20, width - 27]);
                const y = d3.scaleLinear().rangeRound([5, height - 40]);

                x.domain([0, maxTime]);
                y.domain([maxPPP, minPPP]);

                svg.append("g")
                    .call(d3.axisRight(y).ticks(4).tickSize(0))
                    .append("text");

                svg.append("g")
                    .call(d3.axisBottom(x).ticks(4).tickSize(0))
                    .attr("transform", "translate(0," + (height - 35) + ")")
                    .append("text");


                svg.selectAll(".player")
                    .data(pt_data, function (d) {
                        return [d.Player, d.PossG, d.PPP];
                    }).enter()
                    .append("circle")
                    .classed("player", true)
                    .attr("cx", function (d) {
                        return x(d.PossG);
                    })
                    .attr("cy", function (d) {
                        return y(d.PPP);
                    })
                    .attr("r", 3.5)
                    .attr("opacity", 0.3)
                    .style("fill", "grey");
            });

            player_list.sort();

            let player_select = $("#player-select");

            player_select.append(($('<option></option>').val('').html('')));
            $.each(player_list, function (i, d) {
                player_select.append(($('<option></option>').val(d).html(d)));
            });

            player_select.change(function () {
                let player = this.value;
                d3.selectAll(".player")
                    .transition().duration(1000)
                    .attr("r", function (d) {
                        if (d.Player === player) {
                            return 5;
                        } else {
                            return 3.5;
                        }
                    })
                    .attr("opacity", function (d) {
                        if (d.Player === player) {
                            return 1;
                        } else {
                            return 0.3;
                        }
                    })
                    .style("fill", function (d) {
                        if (d.Player === player) {
                            return "blue";
                        } else {
                            return "grey";
                        }
                    });
            });

        })

    .error(function (error, msg) {
        console.log(error);
        console.log(msg);
    });

});
