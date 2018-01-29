from util.nba_stats import PlayerAdvancedGameLogs, GeneralPlayerStats
from util.format import get_year_string
from util.reddit import print_reddit_table
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go


stat_to_graph = 'PTS'

data_override = True
normalize_for_possessions = False

logs = PlayerAdvancedGameLogs()
general_stats = GeneralPlayerStats()


def get_trace_for_year(season, num_games_filter=50, num_players_filter=10, min_played_filter=20, is_multi_year=False):
    base_log_df = logs.get_data({'Season': season, 'MeasureType': 'Base'}, override_file=data_override)
    advanced_log_df = logs.get_data({'Season': season, 'MeasureType': 'Advanced'}, override_file=data_override)
    advanced_log_df = advanced_log_df[['PLAYER_ID', 'GAME_ID', 'PACE']]

    merge_cols = ['PLAYER_ID', 'GAME_ID']
    log_df = pd.merge(advanced_log_df, base_log_df, on=merge_cols)

    log_df = log_df[log_df.MIN >= min_played_filter]
    if normalize_for_possessions:
        log_df['POSS'] = log_df['MIN'] * (log_df['PACE'] / 48)
        log_df[stat_to_graph] = (log_df[stat_to_graph] / log_df['POSS']) * 100

    stat_df = general_stats.get_data({'Season': season, 'PerMode': 'PerGame'}, override_file=data_override)

    stat_df = stat_df[stat_df.GP > num_games_filter]
    stat_df = stat_df.sort_values(by=stat_to_graph, ascending=False)
    top_scorers = stat_df.head(num_players_filter).PLAYER_NAME.unique()
    log_df = log_df[log_df.PLAYER_NAME.isin(top_scorers)]
    if is_multi_year:
        log_df['DISPLAY_NAME'] = log_df.PLAYER_NAME.apply(lambda x: x.split(' ')[-1]) + ' \'' + season.split('-')[-1]
    else:
        log_df['DISPLAY_NAME'] = log_df.PLAYER_NAME

    traces = []
    for player in top_scorers:
        player_df = log_df[log_df.PLAYER_NAME == player]
        traces.append(
            go.Box(
                y=player_df[stat_to_graph],
                name=player_df.DISPLAY_NAME.iloc[0],
                boxpoints='all',
                whiskerwidth=1,
                jitter=0.5,
                showlegend=False,
                line=dict(
                    width=1
                )
            )
        )
    traces.sort(key=lambda x: (x.y.quantile(0.75) - x.y.quantile(0.25)))
    # traces.sort(key=lambda x: (x.y.std() / x.y.mean()))
    return traces


def get_traces_for_multiple_years(year_range):
    traces = []
    for y in year_range:
        traces.extend(get_trace_for_year(get_year_string(y), is_multi_year=True))
    traces.sort(key=lambda z: (z.y.std() / z.y.mean()))
    return traces


def plot_traces(traces):
    layout = go.Layout(
        title=stat_to_graph + ' Consistency'
    )

    fig = go.Figure(
        data=traces,
        layout=layout
    )

    py.plot(
        fig,
        filename='Consistency All Time'
    )


def build_consistency_df_from_traces(traces):
    consistency_data = []
    for tr in traces:
        consistency_data.append({
            'Player': tr.name,
            'Mean': tr.y.mean(),
            'Std': tr.y.std(),
            'Std/Mean': tr.y.std() / tr.y.mean(),
            'Min': tr.y.min(),
            'Max': tr.y.max(),
            'Q1': tr.y.quantile(.25),
            'Q3': tr.y.quantile(.75)
        })
    return pd.DataFrame(consistency_data)


num_players = 20
# t = get_traces_for_multiple_years(range(1996, 2018))
t = get_trace_for_year('2017-18', num_games_filter=20, num_players_filter=num_players)
df = build_consistency_df_from_traces(t)
print_reddit_table(df, df.columns)
# a = t[int(-((num_players/2) + 1)):]
# a = a[::-1]
# b = t[0:int(num_players/2)]
# b = b[::-1]
# c = a+b
plot_traces(t)
