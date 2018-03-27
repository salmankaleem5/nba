$(document).ready(function () {

    var home_abb = null,
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

    var courtSelection = d3.select("#shot-chart");

    var max_size = 1000;
    var court_size = Math.min($(window).width(), $(window).height(), max_size);

    var court = d3.court().width(court_size);
    courtSelection.call(court);

    var players = [];

    $.getJSON("./data/shots.json", function (json) {
        var data = json;
        var x = {};
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
        });

        //$('#player-select').append($('<option></option>').val('all').html('all'));
        $('#offense-player-select').append($('<option></option>').val('All').html('All'));
        $('#defense-player-select').append($('<option></option>').val('All').html('All'));
        $.each(players, function (i, p) {
            $('#player-select').append($('<option></option>').val(p).html(p));
            $('#offense-player-select').append($('<option></option>').val(p).html(p));
            $('#defense-player-select').append($('<option></option>').val(p).html(p));
        });

        $('#player-select').change(function () {
            var player = $('#player-select option:selected').val();
            var player_data = data.filter(function (d) {
                return d.player == player;
            });
            var shots = d3.shots().shotRenderThreshold(1).displayToolTips(true).displayType("scatter");
            courtSelection.datum(player_data).call(shots);
        });

        $('#player-select').val($('#player-select option:first').val()).change();
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

    $.fn.dataTable.defaults.column.asSorting = ['desc', 'asc'];
});
