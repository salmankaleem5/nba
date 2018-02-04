from util.nba_stats import PlayerAdvancedGameLogs
from util.format import get_year_string
import pandas as pd

import plotly.plotly as py
import plotly.graph_objs as go


players = {
    'Ryan Anderson': {
        'id': '201583',
        'years': range(2012, 2016)
    },
    'Jrue Holiday': {
        'id': '201950',
        'years': range(2013, 2018)
    },
    'Chris Paul': {
        'id': '101108',
        'years': range(2005, 2011)
    },
    'David West': {
        'id': '2561',
        'years': range(2003, 2011)
    },
    'Anthony Davis': {
        'id': '203076',
        'years': range(2012, 2018)
    }
}


game_ep = PlayerAdvancedGameLogs()
teams = ['NOP', 'NOH', 'NOK']

traces = []

for player in players:
    player_game_log = pd.DataFrame()
    for year in players[player]['years']:
        year_string = get_year_string(year)
        player_year_game_log = game_ep.get_data({
            'PlayerID': players[player]['id'],
            'Season': year_string
        })
        player_year_game_log = player_year_game_log[player_year_game_log['TEAM_ABBREVIATION'].isin(teams)]
        player_game_log = player_game_log.append(player_year_game_log)

    career_points = 0
    games = 0
    player_data = {
        'games': [],
        'points': []
    }
    for ix, game in player_game_log.iterrows():
        career_points += game['PTS']
        games += 1
        player_data['games'].append(games)
        player_data['points'].append(career_points)

    traces.append(go.Scatter(
        x=player_data['games'],
        y=player_data['points'],
        mode='lines',
        name=player
    ))

py.plot(traces, filename='AD Leading Scorer')
