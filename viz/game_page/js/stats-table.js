function create_stats_table() {

    var table = null;
    $.getJSON("./data/stats.json", function (json) {
        table = $("#stats-table").DataTable({
            data: json,
            order: [[1, "desc"], [2, "desc"]],
            paging: false,
            columns: [
                {title: 'Name', data: 'player'},
                {title: 'Team', data: 'TEAM_ABBREVIATION'},
                {title: 'Min', data: 'MIN'},
                {title: "Points", data: 'pts'},
                {title: "True Attempts", data: 'tsa', visible: false, name: 'tsa'},
                {
                    title: "True Efficiency",
                    data: 'eff',
                    render: function (data) {
                        return Math.round(data * 10) / 10 + '%';
                    },
                    visible: false,
                    name: 'eff'
                },
                // {title: 'And-1', data: 'and_one', visible: false, name: 'and-one'},
                // {title: '2pt Ft', data: '2pt_ft', visible: false, name: '2pt-ft'},
                // {title: '3pt Ft', data: '3pt_ft', visible: false, name: '3pt-ft'},
                {
                    title: 'Free Throws',
                    data: null,
                    render: function (data) {
                        var attempts = data['and_one'] + data['2pt_ft'] + data['3pt_ft'] + data['tech_ft'];
                        if (attempts > 0) {
                            return data['ftm'] + '/' + attempts + ' (' + Math.round(data['ftm'] / attempts * 1000) / 10 + '%)';
                        }
                        else {
                            return data['ftm'] + '/' + attempts + ' (0%)';
                        }
                    },
                    visible: false,
                    name: 'ft'
                },
                {
                    title: '2pt Fg',
                    data: null,
                    render: function (data) {
                        if (data['2pt_fga'] > 0) {
                            return data['2pt_fgm'] + '/' + data['2pt_fga'] + ' (' + Math.round(data['2pt_fgm'] / data['2pt_fga'] * 1000) / 10 + '%)';
                        }
                        else {
                            return data['2pt_fgm'] + '/' + data['2pt_fga'] + ' (0%)';
                        }
                    },
                    visible: false,
                    name: '2pt-fgm'
                },
                {
                    title: '3pt Fg',
                    data: null,
                    render: function (data) {
                        if (data['3pt_fga'] > 0) {
                            return data['3pt_fgm'] + '/' + data['3pt_fga'] + ' (' + Math.round(data['3pt_fgm'] / data['3pt_fga'] * 1000) / 10 + '%)';
                        }
                        else {
                            return data['3pt_fgm'] + '/' + data['3pt_fga'] + ' (0%)';
                        }
                    },
                    visible: false,
                    name: '3pt-fgm'
                },
                {title: 'Ast', data: 'ast'},
                {title: 'Passes Made', data: 'PASSES_MADE', visible: false, name: 'passes'},
                {title: 'Potential Ast', data: 'POTENTIAL_AST', visible: false, name: 'potential-ast'},
                {title: 'Ast Pts', data: 'ast_pts', visible: false, name: 'ast-pts'},
                {title: 'Touches', data: 'FRONT_CT_TOUCHES'},
                {
                    title: 'Seconds of Poss',
                    data: 'TIME_OF_POSS',
                    render: function (data) {
                        return data * 60;
                    },
                    visible: false,
                    name: 'time-of-poss'
                },
                {title: 'Elbow Touch', data: 'ELBOW_TOUCHES', visible: false, name: 'elbow'},
                {title: 'Post Touch', data: 'POST_TOUCHES', visible: false, name: 'post'},
                {title: 'Paint Touch', data: 'PAINT_TOUCHES', visible: false, name: 'paint'},
                {title: 'Reb', data: 'REB'},
                {title: 'Box Outs', data: 'BOX_OUTS', visible: false, name: 'box-outs'},
                {
                    title: 'OReb / Chances',
                    data: null,
                    render: function (data) {
                        var adj_chances = data['OREB_CHANCES'] - data['OREB_CHANCE_DEFER'];
                        if (adj_chances > 0) {
                            return data['oreb'] + '/' + (adj_chances) + ' (' + Math.round(data['oreb'] / adj_chances * 1000) / 10 + '%)';
                        } else {
                            return '0/0 (0%)';
                        }
                    },
                    visible: false,
                    name: 'oreb'
                },
                {
                    title: 'DReb / Chances',
                    data: null,
                    render: function (data) {
                        var adj_chances = data['DREB_CHANCES'] - data['DREB_CHANCE_DEFER'];
                        if (adj_chances > 0) {
                            return data['dreb'] + '/' + (adj_chances) + ' (' + Math.round(data['oreb'] / adj_chances * 1000) / 10 + '%)';
                        } else {
                            return '0/0 (0%)';
                        }
                    },
                    visible: false,
                    name: 'dreb'
                },
                {title: 'Stl', data: 'STL'},
                {title: 'Deflections', data: 'DEFLECTIONS', visible: false, name: 'deflections'},
                {title: 'Loose Balls Recovered', data: 'LOOSE_BALLS_RECOVERED', visible: false, name: 'loose-ball'},
                {title: 'Blk', data: 'BLK'},
                {title: 'Rim Fga Defended', data: 'DEF_RIM_FGA', visible: false, name: 'rim-fga'},
                {
                    title: 'Rim Fg% Defended',
                    data: 'DEF_RIM_FG_PCT',
                    render: function (data) {
                        return data + '%';
                    },
                    visible: false,
                    name: 'rim-fgpct'
                },
                {title: 'Screen Ast', data: 'SCREEN_ASSISTS', visible: false, name: 'screen-ast'}
            ]
        });
    });

    $('#scoring-header').click(function () {
        cols = ['tsa', 'eff', 'and-one', '2pt-ft', '3pt-ft', '2pt-fgm', '2pt-fga', '3pt-fgm', '3pt-fga', 'ft'];
        cols.forEach(function (col) {
            var col = table.column(col + ':name');
            col.visible(!col.visible());
        });
    });

    $('#passing-header').click(function () {
        cols = ['potential-ast', 'ast-pts', 'passes'];
        cols.forEach(function (col) {
            var col = table.column(col + ':name');
            col.visible(!col.visible());
        });
    });

    $('#rebounding-header').click(function () {
        cols = ['oreb', 'oreb-chance', 'oreb-pct', 'dreb', 'dreb-chance', 'dreb-pct', 'box-outs'];
        cols.forEach(function (col) {
            var col = table.column(col + ':name');
            col.visible(!col.visible());
        });
    });

    $('#possession-header').click(function () {
        cols = ['time-of-poss', 'elbow', 'post', 'paint'];
        cols.forEach(function (col) {
            var col = table.column(col + ':name');
            col.visible(!col.visible());
        });
    });

    $('#perimeter-d-header').click(function () {
        cols = ['deflections', 'loose-ball'];
        cols.forEach(function (col) {
            var col = table.column(col + ':name');
            col.visible(!col.visible());
        });
    });

    $('#intererio-d-header').click(function () {
        cols = ['rim-fga', 'rim-fgpct'];
        cols.forEach(function (col) {
            var col = table.column(col + ':name');
            col.visible(!col.visible());
        });
    });

    $('#misc-header').click(function () {
        cols = ['screen-ast'];
        cols.forEach(function (col) {
            var col = table.column(col + ':name');
            col.visible(!col.visible());
        });
    });

}
