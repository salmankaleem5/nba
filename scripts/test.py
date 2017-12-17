from util.data import TrackingStats, GeneralTeamStats, get_year_string
from util.reddit import print_reddit_table
import pandas as pd

import plotly.plotly as py
import plotly.graph_objs as go

tracking_stats = TrackingStats()
general_team_stats = GeneralTeamStats()

df = pd.DataFrame()
for s in range(2015, 2018):
    season = get_year_string(s)
    tracking_reb_df = tracking_stats.get_data({'Season': season, 'PtMeasureType': 'Rebounding', 'PerMode': 'Totals',
                                               'PlayerOrTeam': 'Team', 'OpponentTeamID': '0'}, override_file=False)[
        ['TEAM_ID', 'DREB_CHANCE_PCT', 'DREB_CHANCES', 'DREB', 'DREB_CHANCE_DEFER']]
    tracking_reb_df['DEFER_PER_CHANCE'] = tracking_reb_df['DREB_CHANCE_DEFER'] / tracking_reb_df['DREB_CHANCES']
    
    advanced_df = general_team_stats.get_data({'Season': season, 'MeasureType': 'Advanced', 'PerMode': 'Totals'},
                                              override_file=False)[['TEAM_ID', 'TEAM_NAME', 'DREB_PCT']]
    
    opponent_df = general_team_stats.get_data({'Season': season, 'MeasureType': 'Opponent', 'PerMode': 'Totals'},
                                              override_file=False)[['TEAM_ID', 'OPP_FGA', 'OPP_FGM']]
    opponent_df['OPP_FG_MISSED'] = opponent_df['OPP_FGA'] - opponent_df['OPP_FGM']
    opponent_df = opponent_df[['TEAM_ID', 'OPP_FG_MISSED']]
    
    misc_df = general_team_stats.get_data({'Season': season, 'MeasureType': 'Misc', 'PerMode': 'Totals'},
                                          override_file=False)[['TEAM_ID', 'PTS_2ND_CHANCE', 'OPP_PTS_2ND_CHANCE']]
    misc_df['2ND_CHANCE_PTS_DIFF'] = misc_df['PTS_2ND_CHANCE'] - misc_df['OPP_PTS_2ND_CHANCE']
    
    merge_df = pd.merge(tracking_reb_df, advanced_df, on='TEAM_ID')
    merge_df = pd.merge(merge_df, opponent_df, on='TEAM_ID')
    merge_df = pd.merge(merge_df, misc_df, on='TEAM_ID')
    
    merge_df['REB_CHANCES_PER_MISS'] = merge_df['DREB_CHANCES'] / merge_df['OPP_FG_MISSED']
    merge_df = merge_df.sort_values(by='REB_CHANCES_PER_MISS', ascending=True)
    
    uncontested_oreb_data = []
    for t in merge_df['TEAM_ID'].unique():
        team_df = tracking_stats.get_data(
            {'Season': season, 'PtMeasureType': 'Rebounding', 'PerMode': 'Totals', 'PlayerOrTeam': 'Team',
             'OpponentTeamID': t}, override_file=False)[['TEAM_ID', 'OREB_UNCONTEST', 'OREB_CONTEST']]
        uncontested_oreb_data.append({
            'TEAM_ID': t,
            'UNCONTEST_OREB_AGAINST': team_df['OREB_UNCONTEST'].sum(),
            'CONTEST_OREB_AGAINST': team_df['OREB_CONTEST'].sum()
        })
    
    merge_df = pd.merge(merge_df, pd.DataFrame(uncontested_oreb_data), on='TEAM_ID')
    merge_df['UNCONTEST_OREB_PER_MISS'] = merge_df['UNCONTEST_OREB_AGAINST'] / merge_df['OPP_FG_MISSED']
    merge_df['OREB_CONTEST_PCT'] = merge_df['UNCONTEST_OREB_AGAINST'] / (
            merge_df['UNCONTEST_OREB_AGAINST'] + merge_df['CONTEST_OREB_AGAINST'])
    merge_df['CONTESTS_WON'] = (merge_df['OPP_FG_MISSED'] - merge_df['UNCONTEST_OREB_AGAINST']) / merge_df['DREB']
    
    merge_df['YEAR'] = season
    df = df.append(merge_df)

corr = df.corr()['DREB_PCT']

df.to_csv('oreb.csv')


plot_df = df
trace1 = go.Scatter(
    x=plot_df['DREB_CHANCE_PCT'],
    y=plot_df['DREB_PCT'],
    mode='markers'
)

plot_df = df[df['TEAM_NAME'] == 'New Orleans Pelicans']
plot_df = plot_df[plot_df['YEAR'] == '2017-18']
trace2 = go.Scatter(
    x=plot_df['DREB_CHANCE_PCT'],
    y=plot_df['DREB_PCT'],
    text=plot_df['TEAM_NAME'],
    mode='markers'
)

data = [trace1, trace2]

py.plot(data, filename='DREB_CHANCE_PCT')


plot_df = df
trace1 = go.Scatter(
    x=plot_df['REB_CHANCES_PER_MISS'],
    y=plot_df['DREB_PCT'],
    mode='markers'
)

plot_df = df[df['TEAM_NAME'] == 'New Orleans Pelicans']
plot_df = plot_df[plot_df['YEAR'] == '2017-18']
trace2 = go.Scatter(
    x=plot_df['REB_CHANCES_PER_MISS'],
    y=plot_df['DREB_PCT'],
    text=plot_df['TEAM_NAME'],
    mode='markers'
)

data = [trace1, trace2]

py.plot(data, filename='DREB_CHANCES_PER_MISS')


# plot_df = df
# trace1 = go.Scatter(
#     x=plot_df['DEFER_PER_CHANCE'],
#     y=plot_df['DREB_PCT'],
#     mode='markers'
# )
#
# plot_df = df[df['TEAM_NAME'] == 'New Orleans Pelicans']
# plot_df = plot_df[plot_df['YEAR'] == '2017-18']
# trace2 = go.Scatter(
#     x=plot_df['DEFER_PER_CHANCE'],
#     y=plot_df['DREB_PCT'],
#     text=plot_df['TEAM_NAME'],
#     mode='markers'
# )
#
# data = [trace1, trace2]
#
# py.plot(data, filename='DEFER_PER_CHANCE')

None