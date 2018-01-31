from util.data import TrackingStats, ShotChartDetail, PlayByPlay, TeamAdvancedGameLogs, data_dir, file_check
import pandas as pd

tracking_ep = TrackingStats()

drives_df = tracking_ep.get_data({'Season': '2017-18', 'PerMode': 'Totals', 'PtMeasureType': 'Drives'},
                                 override_file=True)

drives_df = drives_df[drives_df['DRIVES'] >= 200]

drives_df['ENDING_PLAY'] = drives_df['DRIVE_AST'] + drives_df['DRIVE_FGA'] + (drives_df['DRIVE_FTA'] * 0.44) + drives_df['DRIVE_TOV']
drives_df['TOTAL_POINTS'] = drives_df['DRIVE_PTS'] + (drives_df['DRIVE_AST'] * 2.3)
drives_df['TS'] = (drives_df['DRIVE_FGA'] + (0.44 * drives_df['DRIVE_FTA'])) / drives_df['DRIVES']
drives_df['EFF'] = drives_df['TOTAL_POINTS'] / drives_df['ENDING_PLAY']

drives_df = drives_df.sort_values(by='TS', ascending=False)
corr = drives_df.corr()
None
#
# def merge_shot_pbp(season, season_type='Regular Season'):
#     play_by_play_endpoint = PlayByPlay()
#     shot_endpoint = ShotChartDetail()
#
#     pbp_df = pd.DataFrame()
#     log = TeamAdvancedGameLogs().get_data({'Season': season, 'SeasonType': season_type}, override_file=True)
#     log = log[log['TEAM_ABBREVIATION'] == 'NOP']
#     games = log.GAME_ID.unique()
#     for g in games:
#         if len(str(g)) < 10:
#             g = '00' + str(g)
#         pbp_df = pbp_df.append(
#             play_by_play_endpoint.get_data({'GameID': g, 'Season': season, 'SeasonType': season_type}))
#
#     pbp_df['GAME_ID'] = '00' + pbp_df['GAME_ID'].astype(str)
#     shots_df = shot_endpoint.get_data({'Season': season, 'SeasonType': season_type}, override_file=True)
#     merge_df = pd.merge(pbp_df, shots_df, left_on=['EVENTNUM', 'GAME_ID', 'PERIOD'],
#                         right_on=['GAME_EVENT_ID', 'GAME_ID', 'PERIOD'], how='outer')
#
#     file_path = data_dir + 'drives.csv'
#     file_check(file_path)
#     merge_df.to_csv(file_path)
#
#
# df = pd.read_csv(data_dir + 'drives.csv')
