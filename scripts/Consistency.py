from util.data import PlayerAdvancedGameLogs, GeneralPlayerStats
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go


stat_to_graph = 'PTS'
season = '2017-18'

num_games_filter = 5
num_players_filter = 10
min_played_filter = 20

data_override = True
normalize = True


logs = PlayerAdvancedGameLogs()
general_stats = GeneralPlayerStats()


base_log_df = logs.get_data({'Season': season, 'MeasureType': 'Base'}, override_file=data_override)
advanced_log_df = logs.get_data({'Season': season, 'MeasureType': 'Advanced'}, override_file=data_override)
advanced_log_df = advanced_log_df[['PLAYER_ID', 'GAME_ID', 'PACE']]

merge_cols = ['PLAYER_ID', 'GAME_ID']
log_df = pd.merge(advanced_log_df, base_log_df, on=merge_cols)

log_df = log_df[log_df.MIN >= min_played_filter]
if normalize:
    log_df['POSS'] = log_df['MIN'] * (log_df['PACE'] / 48)
    log_df[stat_to_graph] = (log_df[stat_to_graph] / log_df['POSS']) * 100

stat_df = general_stats.get_data({'Season': season, 'PerMode': 'PerGame'}, override_file=data_override)

stat_df = stat_df[stat_df.GP > num_games_filter]
stat_df = stat_df.sort_values(by=stat_to_graph, ascending=False)

top_scorers = stat_df.head(num_players_filter).PLAYER_NAME.unique()

traces = []
for player in top_scorers:
    player_df = log_df[log_df.PLAYER_NAME == player]
    traces.append(
        go.Box(
            y=player_df[stat_to_graph],
            name=player,
            boxpoints='all',
            whiskerwidth=1,
            jitter=0.5,
            showlegend=False,
            line=dict(
                width=1
            )
        )
    )

layout = go.Layout(
    title=stat_to_graph + ' Consistency'
)

traces.sort(key=lambda x: x.y.std())

fig = go.Figure(
    data=traces,
    layout=layout
)

py.plot(
    fig,
    filename='Consistency'
)
