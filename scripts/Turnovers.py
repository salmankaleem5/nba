from util.data import PlayByPlay, TeamAdvancedGameLogs, data_dir, file_check, GeneralTeamStats
import pandas as pd

season = '2017-18'
tov_types = ['Bad Pass Turnover', 'Lost Ball Turnover', 'Offensive Foul Turnover', 'Step Out of Bounds Turnover',
             'Traveling Turnover', 'Out of Bounds - Bad Pass Turnover', '3 Second Violation Turnover']
file_path = data_dir + 'Turnovers/data.csv'


def get_tov_pbp_data(override_file=False):
    if override_file or not file_check(file_path):
        pbp_ep = PlayByPlay()
        log_ep = TeamAdvancedGameLogs()

        log_df = log_ep.get_data({'Season': season}, override_file=False)

        season_pbp_df = pd.DataFrame()
        for g in log_df['GAME_ID'].unique():
            g = str(g)
            if len(g) < 10:
                g = '00' + g
            game_df = pbp_ep.get_data({'Season': season, 'GameID': g})
            game_df = game_df[game_df['EVENTMSGTYPE'] == 5]
            season_pbp_df = season_pbp_df.append(game_df)

        season_pbp_df = season_pbp_df.fillna('')
        season_pbp_df.to_csv(file_path)
        return season_pbp_df
    else:
        return pd.read_csv(file_path)


def get_tov_type_data():
    tov_pbp_df = get_tov_pbp_data()
    tov_pbp_df = tov_pbp_df.fillna('')
    tov_type_data = []
    teams = tov_pbp_df['PLAYER1_TEAM_ABBREVIATION'].unique()
    for t in teams:
        if len(t) > 1:
            team_tov_pbp_df = tov_pbp_df[tov_pbp_df['PLAYER1_TEAM_ABBREVIATION'] == t]
            team_tov_type_data = {
                'TEAM_ABBREVIATION': t,
                'TEAM_ID': team_tov_pbp_df['PLAYER1_TEAM_ID'].iloc[0],
                'TOTAL_TOV': 0
            }
            for tov_type in tov_types:
                home_df = team_tov_pbp_df[team_tov_pbp_df['HOMEDESCRIPTION'].str.contains(tov_type)]
                visitor_df = team_tov_pbp_df[team_tov_pbp_df['VISITORDESCRIPTION'].str.contains(tov_type)]
                tov_type_df = home_df.append(visitor_df)
                team_tov_type_data[tov_type] = len(tov_type_df)
                team_tov_type_data['TOTAL_TOV'] += len(tov_type_df)
            tov_type_data.append(team_tov_type_data)

    return pd.DataFrame(tov_type_data)


misc_df = GeneralTeamStats().get_data({'Season': season, 'PerMode': 'Totals', 'MeasureType': 'Misc'},
                                        override_file=False)[['TEAM_ID', 'PTS_OFF_TOV']]

total_df = get_tov_type_data()
total_df = total_df.merge(misc_df, on='TEAM_ID')
total_df['Bad Pass Turnover'] = total_df['Bad Pass Turnover'] - total_df['Out of Bounds - Bad Pass Turnover']
total_df['Live Ball Turnover'] = total_df['Bad Pass Turnover'] + total_df['Lost Ball Turnover']
total_df['Pts_Per_Live_Ball_Tov'] = total_df['PTS_OFF_TOV'] / total_df['Live Ball Turnover']
total_df.to_csv(data_dir + 'Turnovers/total.csv')

pct_df = total_df
for tov_type in tov_types:
    pct_df[tov_type] = round((pct_df[tov_type] / pct_df['TOTAL_TOV']) * 100, 2)
pct_df['Live Ball Turnover'] = round(pct_df['Bad Pass Turnover'] + pct_df['Lost Ball Turnover'], 2)
pct_df.to_csv(data_dir + 'Turnovers/pct.csv')