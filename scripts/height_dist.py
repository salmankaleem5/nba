from util.data import GeneralPlayerStats, PlayerBios
import pandas as pd

import plotly.plotly as py
import plotly.figure_factory as ff

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt


pre_df = PlayerBios().get_data({'Season': '2017-18', 'SeasonType': 'Pre Season'})
pre_df = pre_df[['PLAYER_NAME', 'PLAYER_HEIGHT_INCHES', 'TEAM_ABBREVIATION']]

reg_df = GeneralPlayerStats().get_data({'Season': '2016-17', 'SeasonType': 'Regular Season', 'PerMode': 'Totals'})
reg_df = reg_df[['PLAYER_NAME', 'MIN']]

merge_df = pd.merge(pre_df, reg_df, on='PLAYER_NAME', how='inner')

# hist_data = []
# team_labels = []
#
# for team in merge_df.TEAM_ABBREVIATION.unique():
#     team_df = merge_df[merge_df.TEAM_ABBREVIATION == team]
#     total_min = round(team_df.MIN.sum())
#     height_dist = []
#     for ix, player in team_df.iterrows():
#         min = round(player.MIN)
#         min_pct = int((min / total_min) * 240)
#         for x in range(0, min_pct):
#             height_dist.append(player.PLAYER_HEIGHT_INCHES)
#     hist_data.append(height_dist)
#     team_labels.append(team)

pels_df = merge_df[merge_df.TEAM_ABBREVIATION == 'NOP']
pels_df['ADJ_MIN'] = (pels_df['MIN'] / pels_df['MIN'].sum()) * 48

hist_data = []
for ix, player in pels_df.iterrows():
    min = round(player.ADJ_MIN)
    for ij in range(0, min):
        hist_data.append(player.PLAYER_HEIGHT_INCHES)

num_bins = 50

fig, ax = plt.subplots()

n, bins, patches = ax.hist(hist_data, num_bins)

ax.plot(bins)

plt.show()

# fig = ff.create_distplot(hist_data, team_labels, bin_size=1)
# py.plot(fig, filename='Height Dist')
