from util.data import get_rpm, GeneralPlayerStats, data_dir
from util.reddit import print_reddit_table
import pandas as pd

import plotly.plotly as py
import plotly.graph_objs as go

rpm_df = get_rpm()

base_df = GeneralPlayerStats().get_data({'Season': '2017-18', 'PerMode': 'Totals', 'MeasureType': 'Base'})
base_df = base_df[base_df.MIN >= 200]

merge_df = pd.merge(rpm_df, base_df, left_on=['NAME'], right_on=['PLAYER_NAME'], how='inner')
merge_df.to_csv(data_dir + '3&D.csv')

merge_df['3pt_Rate'] = (merge_df['FG3A'] / merge_df['MIN']) * 48
merge_df['3pt_Pct_Abv_Exp'] = merge_df['FG3_PCT'] - (merge_df['FG3M'].sum() / merge_df['FG3A'].sum())
merge_df['3pt_Rating'] = merge_df['3pt_Rate'] * merge_df['FG3_PCT']
merge_df = merge_df[merge_df['3pt_Rating'] > 1]

merge_df = merge_df[['NAME', 'MIN', '3pt_Rating', 'DRPM']]
merge_df['MIN'] -= merge_df.MIN.min()
merge_df['MIN'] /= merge_df.MIN.max()
merge_df['MIN'] = (merge_df.MIN * 20) + 1

merge_df['3D_Rating'] = ((merge_df['3pt_Rating'] - merge_df['3pt_Rating'].mean()) / merge_df['3pt_Rating'].std()) + (
    (merge_df['DRPM'] - merge_df['DRPM'].mean()) / merge_df['DRPM'].std())

merge_df = merge_df.sort_values(by='3D_Rating', ascending=False)
print_reddit_table(merge_df, ['NAME', '3pt_Rating', 'DRPM', '3D_Rating'])

# traces = []
# trace_df = merge_df
# traces.append(
#     go.Scatter(
#         x=trace_df['DRPM'],
#         y=trace_df['3pt_Rating'],
#         text=trace_df['NAME'],
#         mode='markers',
#         marker=dict(
#             size=trace_df['MIN']
#         )
#     )
# )
#
# trace_df = merge_df.sort_values(by='3D_Rating', ascending=False).head(20)
# traces.append(
#     go.Scatter(
#         x=trace_df['DRPM'],
#         y=trace_df['3pt_Rating'],
#         text=trace_df['NAME'],
#         mode='markers',
#         marker=dict(
#             size=trace_df['MIN']
#         )
#     )
# )
#
# trace_df = merge_df.sort_values(by='3D_Rating', ascending=True).head(20)
# traces.append(
#     go.Scatter(
#         x=trace_df['DRPM'],
#         y=trace_df['3pt_Rating'],
#         text=trace_df['NAME'],
#         mode='markers',
#         marker=dict(
#             size=trace_df['MIN']
#         )
#     )
# )
#
# py.plot(traces, filename='3&D')
