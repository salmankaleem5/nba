function create_stats_table(target, team) {

    let table = null;
    $.getJSON("./data/box_score.json", function (json) {
        console.log(json);
        const team_data = json.filter(function (d) {
           return d.TEAM_ABBREVIATION === team;
        });
        console.log(team_data);
        table = target.DataTable({
            data: team_data,
            order: [[1, "desc"], [2, "desc"]],
            paging: false,
            searching: false,
            columns: [
                {title: 'Name', data: 'PLAYER_NAME'},
                {title: 'Team', data: 'TEAM_ABBREVIATION'},
                {
                  title: 'Min',
                  data: 'MIN',
                  render: function (data, type) {
                    if (type === "display") {
                      return data;
                    } else {
                      return seconds = parseInt(data.split(':')[0]) * 60 + parseInt(data.split(':')[1]);
                    }
                  }
                },
                {title: "Points", data: 'PTS'},
                {title: "True Attempts", data: 'TSA', visible: false, name: 'tsa'},
                {
                    title: "True Efficiency",
                    data: 'EFF',
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
                    render: function (data, type) {
                        let attempts = data['AND_ONE'] + data['2PT_FTA'] + data['3PT_FTA'] + data['TECH_FTA'];
                        if (type === 'display') {
                          if (attempts > 0) {
                              return data['FTM'] + '/' + attempts + ' (' + Math.round(data['FTM'] / attempts * 1000) / 10 + '%)';
                          } else {
                              return data['FTM'] + '/' + attempts + ' (0%)';
                          }
                        } else {
                          return data['FTM'];
                        }
                    },
                    visible: false,
                    name: 'ft'
                },
                {
                    title: '2pt Fg',
                    data: null,
                    render: function (data, type) {
                        if (type === 'display') {
                          if (data['2PT_FGA'] > 0) {
                              return data['2PT_FGM'] + '/' + data['2PT_FGA'] + ' (' + Math.round(data['2PT_FGM'] / data['2PT_FGA'] * 1000) / 10 + '%)';
                          }
                          else {
                              return data['2PT_FGM'] + '/' + data['2PT_FGA'] + ' (0%)';
                          }
                        } else {
                          return data['2PT_FGM'];
                        }
                    },
                    visible: false,
                    name: '2pt-fgm'
                },
                {
                    title: '3pt Fg',
                    data: null,
                    render: function (data, type) {
                        if (type === 'display') {
                          if (data['3PT_FGA'] > 0) {
                              return data['3PT_FGM'] + '/' + data['3PT_FGA'] + ' (' + Math.round(data['3PT_FGM'] / data['3PT_FGA'] * 1000) / 10 + '%)';
                          }
                          else {
                              return data['3PT_FGM'] + '/' + data['3PT_FGA'] + ' (0%)';
                          }
                        } else {
                          return data['3PT_FGM'];
                        }
                    },
                    visible: false,
                    name: '3pt-fgm'
                },
                {title: 'Ast', data: 'AST'},
                {title: 'Passes Made', data: 'PASS', visible: false, name: 'passes'},
                {title: 'Potential Ast', data: 'POTENTIAL_AST', visible: false, name: 'potential-ast'},
                {title: 'Ast Pts', data: 'AST_PTS', visible: false, name: 'ast-pts'},
                {title: 'Touches', data: 'TCHS'},
                {title: 'Reb', data: 'REB'},
                {title: 'Box Outs', data: 'BOX_OUTS', visible: false, name: 'box-outs'},
                {
                    title: 'OReb / Chances',
                    data: null,
                    render: function (data, type) {
                        if (type === 'display') {
                          let adj_chances = data['ORBC'];
                          if (adj_chances > 0) {
                              return data['OREB'] + '/' + (adj_chances) + ' (' + Math.round(data['OREB'] / adj_chances * 1000) / 10 + '%)';
                          } else {
                              return '0/0 (0%)';
                          }
                        } else {
                          return data['OREB'];
                        }
                    },
                    visible: false,
                    name: 'oreb'
                },
                {
                    title: 'DReb / Chances',
                    data: null,
                    render: function (data, type) {
                        if (type === 'display') {
                          let adj_chances = data['DRBC'];
                          if (adj_chances > 0) {
                              return data['DREB'] + '/' + (adj_chances) + ' (' + Math.round(data['DREB'] / adj_chances * 1000) / 10 + '%)';
                          } else {
                              return '0/0 (0%)';
                          }
                        } else {
                          return data['DREB'];
                        }
                    },
                    visible: false,
                    name: 'dreb'
                },
                {title: 'Stl', data: 'STL'},
                {title: 'Deflections', data: 'DEFLECTIONS', visible: false, name: 'deflections'},
                {title: 'Loose Balls Recovered', data: 'LOOSE_BALLS_RECOVERED', visible: false, name: 'loose-ball'},
                {title: 'Blk', data: 'BLK'},
                {
                  title: 'Rim Fga Defended',
                  data: null,
                  visible: false,
                  name: 'rim-fga',
                  render: function (data, type) {
                    if (type === 'display') {
                      if (data['DFGA'] > 0) {
                        return data['DFGM'] + '/' + data['DFGA'] + '(' + Math.round(data['DFGM'] / data['DFGA'] * 1000) / 10 + '%)';
                      } else {
                        return '0/0 (0%)';
                      }
                    } else {
                      return data['DFGA'];
                    }

                  }
                },
                {title: 'Screen Ast', data: 'SCREEN_ASSISTS', visible: false, name: 'screen-ast'}
            ]
        });
    });

    target.find('#scoring-header').click(function () {
        let cols = ['tsa', 'eff', 'and-one', '2pt-ft', '3pt-ft', '2pt-fgm', '2pt-fga', '3pt-fgm', '3pt-fga', 'ft'];
        cols.forEach(function (col) {
            col = table.column(col + ':name');
            col.visible(!col.visible());
        });
    });

    target.find('#passing-header').click(function () {
        let cols = ['potential-ast', 'ast-pts', 'passes'];
        cols.forEach(function (c) {
            let col = table.column(c + ':name');
            col.visible(!col.visible());
        });
    });

    target.find('#rebounding-header').click(function () {
        let cols = ['oreb', 'oreb-chance', 'oreb-pct', 'dreb', 'dreb-chance', 'dreb-pct', 'box-outs'];
        cols.forEach(function (c) {
            let col = table.column(c + ':name');
            col.visible(!col.visible());
        });
    });

    target.find('#possession-header').click(function () {
        let cols = ['time-of-poss', 'elbow', 'post', 'paint'];
        cols.forEach(function (c) {
            let col = table.column(c + ':name');
            col.visible(!col.visible());
        });
    });

    target.find('#perimeter-d-header').click(function () {
        let cols = ['deflections', 'loose-ball'];
        cols.forEach(function (c) {
            let col = table.column(c + ':name');
            col.visible(!col.visible());
        });
    });

    target.find('#intererio-d-header').click(function () {
        let cols = ['rim-fga', 'rim-fgpct'];
        cols.forEach(function (c) {
            let col = table.column(c + ':name');
            col.visible(!col.visible());
        });
    });

    target.find('#misc-header').click(function () {
        let cols = ['screen-ast'];
        cols.forEach(function (c) {
            let col = table.column(c + ':name');
            col.visible(!col.visible());
        });
    });

}
