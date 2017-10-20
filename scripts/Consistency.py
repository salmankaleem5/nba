from util.data import GameLogs, GeneralPlayerStats
import plotly.plotly as py
import plotly.graph_objs as go

stat_to_graph = 'PTS'
season = '2016-17'
num_games_filter = 50
num_players_filter = 10


log_df = GameLogs().get_data({'Season': season})
stat_df = GeneralPlayerStats().get_data({'Season': season, 'PerMode': 'PerGame'})

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
            whiskerwidth=0,
            jitter=1,
            showlegend=False,
            line=dict(
                width=0
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
