from util.nba_stats import GeneralTeamStats
from util.reddit import print_reddit_table
import pandas as pd

import plotly.plotly as py
import plotly.graph_objs as go


first_year = '2016-17'
second_year = '2017-18'
data_override = False

teamStats = GeneralTeamStats()

cols = ['TEAM_NAME', 'OFF_RATING', 'DEF_RATING', 'NET_RATING']
first_year_df = teamStats.get_data({'Season': first_year, 'PerMode': 'Totals', 'MeasureType': 'Advanced'},
                                   override_file=data_override)
second_year_df = teamStats.get_data({'Season': second_year, 'PerMode': 'Totals', 'MeasureType': 'Advanced'},
                                    override_file=data_override)

first_year_df.rename(columns=lambda x: 'FIRST_' + x, inplace=True)
second_year_df.rename(columns=lambda x: 'SECOND_' + x, inplace=True)

merge_df = pd.merge(first_year_df, second_year_df, left_on=['FIRST_TEAM_NAME'],
                    right_on=['SECOND_TEAM_NAME'], how='inner')

df = pd.DataFrame()
df['TEAM'] = merge_df.FIRST_TEAM_NAME

df['FIRST_O'] = (merge_df.FIRST_OFF_RATING - merge_df.FIRST_OFF_RATING.mean()) / merge_df.FIRST_OFF_RATING.std()
df['SECOND_O'] = (merge_df.SECOND_OFF_RATING - merge_df.SECOND_OFF_RATING.mean()) / merge_df.SECOND_OFF_RATING.std()

df['FIRST_D'] = (merge_df.FIRST_DEF_RATING - merge_df.FIRST_DEF_RATING.mean()) / merge_df.FIRST_DEF_RATING.std()
df['SECOND_D'] = (merge_df.SECOND_DEF_RATING - merge_df.SECOND_DEF_RATING.mean()) / merge_df.SECOND_DEF_RATING.std()

df['FIRST_N'] = (merge_df.FIRST_NET_RATING - merge_df.FIRST_NET_RATING.mean()) / merge_df.FIRST_NET_RATING.std()
df['SECOND_N'] = (merge_df.SECOND_NET_RATING - merge_df.SECOND_NET_RATING.mean()) / merge_df.SECOND_NET_RATING.std()

df['O_DIFF'] = df.SECOND_O - df.FIRST_O
df['D_DIFF'] = df.FIRST_D - df.SECOND_D
df['N_DIFF'] = df.SECOND_N - df.FIRST_N

df = df.sort_values(by='N_DIFF', ascending=False)
print_reddit_table(df, ['TEAM', 'O_DIFF', 'D_DIFF', 'N_DIFF'])

trace = go.Scatter(
    x=df['O_DIFF'],
    y=df['D_DIFF'],
    text=df['TEAM'],
    mode='markers'
)
py.plot([trace], filename='Improvement')