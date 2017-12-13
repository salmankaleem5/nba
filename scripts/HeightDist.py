from util.data import TrackingStats, PlayerBios, GeneralPlayerStats
import pandas as pd

import plotly.plotly as py
import plotly.figure_factory as ff

season = '2017-18'
data_refresh = False

bio_df = PlayerBios().get_data({'Season': season}, override_file=data_refresh)[
    ['PLAYER_NAME', 'PLAYER_HEIGHT_INCHES', 'TEAM_ABBREVIATION']]

stats_df = GeneralPlayerStats().get_data({'Season': season, 'PerMode': 'Totals', 'MeasureType': 'Base'},
                                         override_file=data_refresh)[['PLAYER_NAME', 'FGA']]

merge_df = pd.merge(bio_df, stats_df, on='PLAYER_NAME', how='inner')

pels_df = merge_df[merge_df['TEAM_ABBREVIATION'] == 'NOP']
league_df = merge_df[merge_df['TEAM_ABBREVIATION'] == 'GSW']

pels_total_fga = pels_df['FGA'].sum()
pels_height_dist = []
for ix, p in pels_df.iterrows():
    fga_pct = int((p.FGA / pels_total_fga) * 10000)
    for x in range(0, fga_pct):
        pels_height_dist.append(p.PLAYER_HEIGHT_INCHES)

league_total_fga = league_df['FGA'].sum()
league_height_dist = []
for ix, p in league_df.iterrows():
    fga_pct = int((p.FGA / league_total_fga) * 10000)
    for x in range(0, fga_pct):
        league_height_dist.append(p.PLAYER_HEIGHT_INCHES)

hist_data = [pels_height_dist, league_height_dist]
team_labels = ['NOP', 'GSW']

fig = ff.create_distplot(hist_data, team_labels)

py.plot(fig, filename='Height Dist')
