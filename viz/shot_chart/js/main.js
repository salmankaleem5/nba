$(document).ready(function () {

    var players = [];
    var data = null;

    var courtSelection = d3.select("#shot-chart");
    var court = d3.court().width(1000);
    courtSelection.call(court);

    $.getJSON("./data/shots.json", function (json) {
        var data = json;
        var x = {};

        $.each(data, function (i, d) {
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

        $.each(players, function (i, p) {
            $('#player-select').append($('<option></option>').val(p).html(p));
        });

        $('#player-select').change(function () {
            var player = $('#player-select option:selected').val();
            var player_data = data.filter(function (d) {
                return d.player == player;
            });
            var shots = d3.shots().shotRenderThreshold(1).displayToolTips(true).displayType("hexbin");
            courtSelection.datum(player_data).call(shots);
        });

        $('#player-select').val($('#player-select option:first').val()).change();
    });
});
