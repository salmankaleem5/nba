from util.data import PlayByPlay, TeamAdvancedGameLogs, TrackingStats, data_dir, file_check, ShotTracking, \
    GeneralTeamStats, GeneralPlayerStats
import pandas as pd

season = '2017-18'
tov_types = ['Bad Pass Turnover', 'Lost Ball Turnover', 'Offensive Foul Turnover', 'Step Out of Bounds Turnover',
             'Travelling Turnover', 'Out of Bounds - Bad Pass Turnover', 'Turnover: Shot Clock',
             '3 Second Violation Turnover']


def get_tov_pbp_data():
    pbp_ep = PlayByPlay()
    log_ep = TeamAdvancedGameLogs()

    log_df = log_ep.get_data({'Season': season}, override_file=True)

    season_pbp_df = pd.DataFrame()
    for g in log_df['GAME_ID'].unique():
        g = str(g)
        if len(g) < 10:
            g = '00' + g
        game_df = pbp_ep.get_data({'Season': season, 'GameID': g})
        game_df = game_df[game_df['EVENTMSGTYPE'] == 5]
        season_pbp_df = season_pbp_df.append(game_df)

    return season_pbp_df


def get_tov_type_data():
    general_team_ep = GeneralTeamStats()

    tov_pbp_df = get_tov_pbp_data()
    general_df = general_team_ep.get_data({'Season': season, 'PerMode': 'Totals', 'MeasureType': 'Base'},
                                          override_file=True)
    tov_type_data = []
    for ix, t in general_df.iterrows():
        team_tov_type_data = {
            'TEAM_ABBREVIATION': t,
            'TOTAL_TOV': t
        }
        team_tov_pbp_df = tov_pbp_df[tov_pbp_df['PLAYER1_TEAM_ABBREVIATION'] == t.TEAM_ABBREVIATION]
        for tov_type in tov_types:
            home_df = team_tov_pbp_df[team_tov_pbp_df['HOMEDESCRIPTION'].str.contains(tov_type)]
            visitor_df = team_tov_pbp_df[team_tov_pbp_df['VISITORDESCRIPTION'].str.contains(tov_type)]
            tov_type_df = home_df.append(visitor_df)
            team_tov_type_data[tov_type] = len(tov_type_df)
        tov_type_data.append(team_tov_type_data)

    return pd.DataFrame(tov_type_data)


df = get_tov_type_data()
None

