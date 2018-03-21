$(document).ready(function () {

    console.log($(window).height());
    console.log();

    $.getJSON("./data/game_summary.json", function (json) {
      $("#home-score").html(json[0]['PTS']);
      $("#away-score").html(json[1]['PTS']);
      $("#home-logo").attr("src", "./img/" + json[0]['TEAM_ABBREVIATION'] + '.svg');
      $("#away-logo").attr("src", "./img/" + json[1]['TEAM_ABBREVIATION'] + '.svg');
    });

    $.getJSON("./data/rotations.json", function (rotation_data) {
        $.getJSON("./data/score.json", function (score_data) {
            plot_rotation_heat_map(rotation_data, score_data);
        });

    });

    var courtSelection = d3.select("#shot-chart");
    var court = d3.court().width(Math.min($(window).width(), $(window).height()) * 1.5);
    courtSelection.call(court);

    players = [];

    $.getJSON("./data/shots.json", function (json) {
        data = json;
        x = {};
        $.each(data, function (i, d) {
            if ($.inArray(this.shooter, players) === -1) {
                players.push(this.shooter);
                x[this.shooter] = 1;
            }
            else {
                x[this.shooter]++;
            }
        });
        players.sort(function (a, b) {
            return x[b] - x[a];
        })

        //$('#player-select').append($('<option></option>').val('all').html('all'));
        $('#offense-player-select').append($('<option></option>').val('All').html('All'));
        $('#defense-player-select').append($('<option></option>').val('All').html('All'));
        $.each(players, function (i, p) {
            $('#player-select').append($('<option></option>').val(p).html(p));
            $('#offense-player-select').append($('<option></option>').val(p).html(p));
            $('#defense-player-select').append($('<option></option>').val(p).html(p));
        });

        $('#player-select').val($('#player-select option:first').val()).change();
    });

    $('#player-select').change(function () {
        player = $('#player-select option:selected').val();
        player_data = data.filter(function (d) {
            return d.player == player;
        });
        var shots = d3.shots().shotRenderThreshold(1).displayToolTips(true).displayType("scatter");
        courtSelection.datum(player_data).call(shots);
    });

    $.getJSON("./data/matchups.json", function(json) {
      create_matchups_table();
    });

    create_stats_table();

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
});
