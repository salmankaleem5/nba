from util.data_scrappers.nba_stats import GeneralPlayerStats
from util.merge_shot_pbp import merge_shot_pbp_for_season
import pandas as pd

import plotly.plotly as py
import plotly.graph_objs as go

year = '2017-18'
min_filter = 0

df = merge_shot_pbp_for_season(year)

guards_df = GeneralPlayerStats().get_data(
    {'Season': year, 'PlayerPosition': 'C', 'PerMode': 'Totals'})
guards_df = guards_df[guards_df['MIN'] >= min_filter]

guards = guards_df['PLAYER_NAME'].tolist()

data = []
for g in guards:
    g_df = df[df['PLAYER1_NAME'] == g]

    if len(g_df) == 0:
        continue

    team_name = g_df['PLAYER1_TEAM_ABBREVIATION'].iloc[0]
    total_attempts = len(g_df)

    g_df = g_df[g_df['SHOT_ZONE_BASIC'] == 'Restricted Area']
    restricted_area_attempts = len(g_df)

    g_df = g_df[g_df['SHOT_MADE_FLAG'] == 1]
    restricted_area_makes = len(g_df)

    g_df = g_df[g_df['PLAYER2_ID'] != 0]
    restricted_area_assisted = len(g_df)

    data.append({
        'player': g,
        'team': team_name,
        'total fga': total_attempts,
        'ra fga': restricted_area_attempts,
        'ra fgm': restricted_area_makes,
        'ra fg pct': (restricted_area_makes / restricted_area_attempts) * 100 if restricted_area_makes > 0 else 0,
        'ra ast': restricted_area_assisted,
        'pct fga ra': (restricted_area_attempts / total_attempts) * 100 if total_attempts > 0 else 0,
        'pct ra ast': (restricted_area_assisted / restricted_area_makes) * 100 if restricted_area_makes > 0 else 0
    })

data_df = pd.DataFrame(data)
data_df = data_df[data_df['ra fga'] >= 1]
data_df = data_df.sort_values(by='pct ra ast', ascending=False)


team_data = []
teams = data_df['team'].unique()
for t in teams:
    t_df = data_df[data_df['team'] == t]
    team_data.append({
        'team': t,
        'total fga': t_df['total fga'].sum(),
        'ra fga': t_df['ra fga'].sum(),
        'ra fgm': t_df['ra fgm'].sum(),
        'ra fg pct': (t_df['ra fgm'].sum() / t_df['ra fga'].sum()) * 100,
        'ra ast': t_df['ra ast'].sum(),
        'pct fga ra': (t_df['ra fga'].sum() / t_df['total fga'].sum()) * 100,
        'pct ra ast': (t_df['ra ast'].sum() / t_df['ra fgm'].sum()) * 100
    })

team_df = pd.DataFrame(team_data)
team_df = team_df.sort_values(by='pct ra ast', ascending=False)

trace_df = team_df[team_df['team'] != 'NOP']
trace1 = go.Scatter(
    x=trace_df['pct fga ra'],
    y=trace_df['pct ra ast'],
    text=trace_df['team'],
    mode='markers'
)
trace_df = team_df[team_df['team'] == 'NOP']
trace2 = go.Scatter(
    x=trace_df['pct fga ra'],
    y=trace_df['pct ra ast'],
    text=trace_df['team'],
    mode='markers'
)


py.plot([trace1, trace2], filename='RA Centers')
