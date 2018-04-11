$(document).ready(function () {

    let home_abb = null,
        away_abb = null;

    $.getJSON("./data/game_summary.json", function (json) {
        $("#home-score").html(json[0]['PTS']);
        $("#away-score").html(json[1]['PTS']);
        $("#home-logo").attr("src", "./img/" + json[0]['TEAM_ABBREVIATION'] + '.png');
        $("#away-logo").attr("src", "./img/" + json[1]['TEAM_ABBREVIATION'] + '.png');

        home_abb = json[0]['TEAM_ABBREVIATION'];
        away_abb = json[1]['TEAM_ABBREVIATION'];
    });

    $.getJSON("./data/rotations.json", function (rotation_data) {
        $.getJSON("./data/score.json", function (score_data) {
            plot_rotation_heat_map(rotation_data, score_data, home_abb, away_abb);
        });

    });

    const max_size = 1000,
        court_size = Math.min($(window).width(), $(window).height(), max_size);

    const courtSelection1 = d3.select("#shot-chart1"),
        courtSelection2 = d3.select("#shot-chart2"),
        court = d3.court().width(court_size);

    courtSelection1.call(court);
    courtSelection2.call(court);

    $.getJSON("./data/shots.json", function (data) {
        let teams = {};
        let x = {};
        $.each(data, function () {
            if ($.inArray(this.shooting_team, Object.keys(teams)) === -1) {
                teams[this.shooting_team] = {'players': []};
            }
            if ($.inArray(this.shooter, teams[this.shooting_team]['players']) === -1) {
                teams[this.shooting_team]['players'].push(this.shooter);
                x[this.shooter] = 1;
            }
            else {
                x[this.shooter]++;
            }
        });

        for (let team in teams) teams[team]['players'].sort(function (a, b) {
            return x[b] - x[a];
        })

        const player_select1 = $('#player-select1'),
            player_select2 = $('#player-select2');

        player_select1.append($('<option></option>').val(Object.keys(teams)[0]).html(Object.keys(teams)[0]));
        $.each(teams[Object.keys(teams)[0]]['players'], function (i, p) {
            player_select1.append($('<option></option>').val(p).html(p));
        });

        player_select2.append($('<option></option>').val(Object.keys(teams)[1]).html(Object.keys(teams)[1]));
        $.each(teams[Object.keys(teams)[1]]['players'], function (i, p) {
            player_select2.append($('<option></option>').val(p).html(p));
        });

        player_select1.change(function () {
            let player = $('#player-select1 option:selected').val();
            let player_data = data.filter(function (d) {
                if (player.length > 3) {
                    return d.player === player;
                } else {
                    return (d.shooting_team === player) & (d.player !== d.assist);
                }
            });
            let shots = d3.shots().shotRenderThreshold(1).displayToolTips(true).displayType("scatter");
            courtSelection1.datum(player_data).call(shots);
        });

        player_select2.change(function () {
            let player = $('#player-select2 option:selected').val();
            let player_data = data.filter(function (d) {
                if (player.length > 3) {
                    return d.player === player;
                } else {
                    return (d.shooting_team === player) & (d.player !== d.assist);
                }
            });
            let shots = d3.shots().shotRenderThreshold(1).displayToolTips(true).displayType("scatter");
            courtSelection2.datum(player_data).call(shots);
        });

        player_select1.val($('#player-select1 option:first').val()).change();
        player_select2.val($('#player-select2 option:first').val()).change();

        let offensive_player_select = $('#offense-player-select');
        let defensive_player_select = $('#defense-player-select');


        offensive_player_select.append($('<option></option>').val('All').html('All'));
        defensive_player_select.append($('<option></option>').val('All').html('All'));
        for (let team in teams) {
            $.each(teams[team]['players'], function (i, p) {
                offensive_player_select.append($('<option></option>').val(p).html(p));
                defensive_player_select.append($('<option></option>').val(p).html(p));
            });
        }

        create_stats_table($("#stats-table1"), Object.keys(teams)[0]);
        create_stats_table($("#stats-table2"), Object.keys(teams)[1]);
    });

    $.getJSON("./data/matchups.json", function (json) {
        create_matchups_table();
    });

    $('#rotations-toggle').change(function () {
        if (!this.checked) {
            $('.hour, .legend').hide();
        } else {
            $('.hour, .legend').show();
        }
    });

    $('#point-diff-toggle').change(function () {
        if (!this.checked) {
            $('.point-diff').hide();
        } else {
            $('.point-diff').show();
        }
    });

    $.fn.dataTable.defaults.column.asSorting = ['desc', 'asc'];
});
