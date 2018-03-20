function create_matchups_table() {

    var table = null;
    $.getJSON("./data/matchups.json", function (json) {
        table = $("#match-up-table").DataTable({
            data: json,
            order: [[2, "desc"]],
            paging: true,
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
}