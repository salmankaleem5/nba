from util.data_scrappers.nba_stats import ShotChartDetail

from util.format import get_year_string
import pandas as pd
import numpy as np

import plotly.plotly as py
import plotly.graph_objs as go

player_name = 'E\'Twaun Moore'
player_id = '203121'
year_range = range(2012, 2018)

shots_ep = ShotChartDetail()

df = pd.DataFrame()
for y in year_range:
    year = get_year_string(y)
    print(year)
    year_df = shots_ep.get_data({
        'ContextMeasure': 'FG3A',
        'PlayerID': player_id,
        'Season': year
    }, override_file=True)
    if len(year_df) > 0:
        year_df = year_df.sort_values(by=['GAME_ID', 'GAME_EVENT_ID'])
        df = df.append(year_df)

df['SHOT_MADE_FLAG'] = df['SHOT_MADE_FLAG'] * 100

rolling_avg = pd.rolling_mean(df['SHOT_MADE_FLAG'], 100).tolist()[99:]
player_data = {
    'Min': min(rolling_avg),
    'Max': max(rolling_avg),
    'Std': np.std(rolling_avg)
}

print(pd.DataFrame([player_data]))


trace = go.Scatter(
    x=list(range(100, len(rolling_avg) + 100)),
    y=rolling_avg
)

py.plot([trace], filename=player_name + ' 3PT Rolling Average')
