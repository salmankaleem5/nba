from util.data import TrackingStats, GeneralTeamStats
import plotly.plotly as py
import plotly.graph_objs as go

season = '2017-18'
data_override = False

trackingStats = TrackingStats()
generalTeamStats = GeneralTeamStats()

rebounding_df = trackingStats.get_data(
    {'Season': season, 'PlayerOrTeam': 'Team', 'PerMode': 'PerGame', 'PtMeasureType': 'Rebounding'},
    override_file=data_override)
advanced_stats_df = generalTeamStats.get_data({'Season': season, 'PerMode': 'Totals', 'MeasureType': 'Advanced'},
                                              override_file=data_override)


def plot_chances_vs_pct(league_df):
    league_trace = go.Scatter(
        x=league_df.OREB_CHANCES,
        y=league_df.OREB_CHANCE_PCT,
        text=league_df.TEAM_ABBREVIATION,
        mode='markers'
    )

    fig = dict(data=[league_trace, pelicans_trace])
    py.plot(fig, filename='Offensive Rebounding')
