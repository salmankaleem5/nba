function create_matchups_table() {

    var table = null;
    $.getJSON("./data/matchups.json", function (json) {
        table = $("#match-up-table").DataTable({
            data: json,
            order: [[2, "desc"]],
            paging: true,
            searching: true,
            columns: [
                {title: 'Offensive Player', data: 'OFF_PLAYER_NAME'},
                {title: 'Defensive Player', data: 'DEF_PLAYER_NAME'},
                {title: 'Possessions', data: 'POSS'},
                {title: 'Player Points', data: 'PLAYER_PTS'},
                {title: 'Team Points', data: 'TEAM_PTS'},
                {
                    title: 'Player 2FG',
                    data: null,
                    render: function (data) {
                        return String(data.FGM - data.FG3M) + '/' + String(data.FGA - data.FG3A);
                    }
                },
                {
                    title: 'Player 3FG',
                    data: null,
                    render: function (data) {
                        return String(data.FG3M) + '/' + String(data.FG3A);
                    }
                },
                {
                    title: 'Player efg%',
                    data: null,
                    render: function (data) {
                        var three_pts = 3 * data.FG3M,
                            two_pts = 2 * (data.FGM - data.FG3M);
                        if (data.FGA > 0) {
                            return (Math.round(((three_pts + two_pts) / data.FGA) * 1000) / 20 + '%');
                        } else {
                            return '0%';
                        }
                    }
                },
                {
                    title: 'Team ORtg',
                    data: null,
                    render: function (data) {
                        return Math.round((data.TEAM_PTS / data.POSS) * 1000) / 10;
                    }
                }
            ]
        })
    })

    $.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
        var o_player = $('#offense-player-select').val();
        var d_player = $('#defense-player-select').val();
        var op_data = data[0];
        var dp_data = data[1];

        if ( ( o_player == op_data || o_player == 'All' ) && (d_player == dp_data || d_player == 'All') )
        {
            return true;
        }
        return false;
    })

    $('#offense-player-select, #defense-player-select').change(function () {
      table.draw();
    });

}
