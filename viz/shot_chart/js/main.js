$(document).ready(function () {


    $.getJSON("./data/shots.json", function (json) {
        let x = {},
            players = [];

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

        plot_shot_chart();

        let player_select = $('#player-select');

        $.each(players, function (i, p) {
            player_select.append($('<option></option>').val(p).html(p));
        });

        player_select.change(function () {
            let player = $('#player-select option:selected').val(),
                player_data = data.filter(function (d) {
                    return d.player === player;
                });
        });

        player_select.val($('#player-select option:first').val()).change();



    });
});
