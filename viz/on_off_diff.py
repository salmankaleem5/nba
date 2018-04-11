import pandas as pd
from util.format import get_year_string, get_display_name, print_reddit_table
from util.data_scrappers.nba_stats import OnOffSummary

import plotly.plotly as py
import plotly.graph_objs as go


def plot_best_worst_on_offs():
    on_off_ep = OnOffSummary()

    df = pd.DataFrame()
    for year in range(2007, 2018):
        year_string = get_year_string(year)
        df = df.append(on_off_ep.get_data_for_all_teams(year_string, override_file=False))

    df = df.sort_values(by='NET_DIFF', ascending=False)
    df['DISPLAY'] = get_display_name(df['VS_PLAYER_NAME'], df['YEAR'])

    traces = []

    reddit_df = pd.DataFrame()

    trace_df = df
    traces.append(
        go.Scatter(
            x=trace_df['DEF_DIFF'],
            y=trace_df['OFF_DIFF'],
            text=trace_df['DISPLAY'],
            mode='markers'
        )
    )

    trace_df = df.head(10)
    reddit_df = reddit_df.append(trace_df)
    traces.append(
        go.Scatter(
            x=trace_df['DEF_DIFF'],
            y=trace_df['OFF_DIFF'],
            text=trace_df['DISPLAY'],
            mode='markers'
        )
    )

    df = df.sort_values(by='NET_DIFF', ascending=True)
    trace_df = df.head(10)
    reddit_df = reddit_df.append(trace_df)
    traces.append(
        go.Scatter(
            x=trace_df['DEF_DIFF'],
            y=trace_df['OFF_DIFF'],
            text=trace_df['DISPLAY'],
            mode='markers'
        )
    )

    df = df.sort_values(by='OFF_DIFF', ascending=False)
    trace_df = df.head(10)
    reddit_df = reddit_df.append(trace_df)
    traces.append(
        go.Scatter(
            x=trace_df['DEF_DIFF'],
            y=trace_df['OFF_DIFF'],
            text=trace_df['DISPLAY'],
            mode='markers'
        )
    )

    df = df.sort_values(by='OFF_DIFF', ascending=True)
    trace_df = df.head(10)
    reddit_df = reddit_df.append(trace_df)
    traces.append(
        go.Scatter(
            x=trace_df['DEF_DIFF'],
            y=trace_df['OFF_DIFF'],
            text=trace_df['DISPLAY'],
            mode='markers'
        )
    )

    df = df.sort_values(by='DEF_DIFF', ascending=False)
    trace_df = df.head(10)
    reddit_df = reddit_df.append(trace_df)
    traces.append(
        go.Scatter(
            x=trace_df['DEF_DIFF'],
            y=trace_df['OFF_DIFF'],
            text=trace_df['DISPLAY'],
            mode='markers'
        )
    )

    df = df.sort_values(by='DEF_DIFF', ascending=True)
    trace_df = df.head(10)
    reddit_df = reddit_df.append(trace_df)
    traces.append(
        go.Scatter(
            x=trace_df['DEF_DIFF'],
            y=trace_df['OFF_DIFF'],
            text=trace_df['DISPLAY'],
            mode='markers'
        )
    )

    py.plot(traces, filename='OnOff')

    reddit_df = reddit_df.sort_values(by='NET_DIFF', ascending=False)
    print_reddit_table(reddit_df, ['VS_PLAYER_NAME', 'YEAR', 'TEAM_ABBREVIATION', 'OFF_DIFF', 'DEF_DIFF', 'NET_DIFF'])
