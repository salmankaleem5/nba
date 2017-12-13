from util.data import get_merged_shot_pbp_data, get_year_string, GeneralPlayerStats
import pandas as pd
import numpy as np

import plotly.plotly as py
import plotly.graph_objs as go

general_df = GeneralPlayerStats().get_data({'Season': '2017-18', 'MeasureType': 'Base'}, override_file=False)
general_df = general_df.sort_values(by='FG3A', ascending=False)

players = general_df.head(25).PLAYER_NAME.tolist()

df = pd.DataFrame()
for y in range(1996, 2018):
    year = get_year_string(y)
    print(year)
    year_df = get_merged_shot_pbp_data(year)
    df = df.append(year_df)

player_data = []
for p in players:
    player_df = df[df.PLAYER1_NAME == p]
    player_df = player_df[player_df.SHOT_TYPE == '3PT Field Goal']

    player_df['SHOT_MADE_FLAG'] = player_df['SHOT_MADE_FLAG'] * 100

    rolling_avg = pd.rolling_mean(player_df['SHOT_MADE_FLAG'], 100).tolist()[99:]
    player_data.append({
        'Player': p,
        'Min': min(rolling_avg),
        'Max': max(rolling_avg),
        'Std': np.std(rolling_avg)
    })

print(pd.DataFrame(player_data))


# trace = go.Scatter(
#     x=list(range(0, len(rolling_avg))),
#     y=rolling_avg
# )
#
# py.plot([trace], filename='LeBron 3PT Rolling Average')
