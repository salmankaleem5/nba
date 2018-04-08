from util.data_scrappers.nba_stats import TeamAdvancedGameLogs
from util.format import get_year_string
import plotly.plotly as py
import plotly.graph_objs as go

game_log_ep = TeamAdvancedGameLogs()

traces = []
for year in range(2000, 2018):
    year_string = get_year_string(year)

    year_game_log = game_log_ep.get_data({'Season': year_string}, override_file=False)
    year_game_log.sort_values(by='GAME_DATE')

    teams = year_game_log['TEAM_ABBREVIATION'].unique()
    for team in teams:
        team_year_game_log = year_game_log[year_game_log['TEAM_ABBREVIATION'] == team]
        total_threes_made = 0
        threes_made_by_game = []
        for ix, game in team_year_game_log.iterrows():
            total_threes_made += game.FG3M
            threes_made_by_game.append(total_threes_made)
        traces.append(
            go.Scatter(
                x=list(range(1, len(team_year_game_log) + 1)),
                y=threes_made_by_game,
                line=dict(
                    color='bcbcbc'
                ),
                name=team + ' ' + year_string,
                showlegend=False
            )
        )

traces.sort(key=lambda x: x.y[-1] / len(x.x))

fig = dict(data=traces)
py.plot(fig, filename='Team 3 Pointers')
