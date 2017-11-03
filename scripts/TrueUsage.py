from util.data import GeneralPlayerStats, TrackingStats
import pandas as pd


year = '2017-18'
data_override = True


generalStats = GeneralPlayerStats()
trackingStats = TrackingStats()


base_cols = ['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'TEAM_ID', 'PTS', 'TOV']
base_df = generalStats.get_data({'Season': year, 'PerMode': 'Totals', 'MeasureType': 'Base'},
                                override_file=data_override)[base_cols]
advanced_cols = ['PLAYER_ID', 'TEAM_ID', 'PACE', 'TS%']
advanced_df = generalStats.get_data({'Season': year, 'PerMode': 'Totals', 'MeasureType': 'Advanced'},
                                    override_file=data_override)[advanced_cols]

passing_cols = ['PLAYER_ID', 'TEAM_ID', 'POTENTIAL_AST', 'AST_PTS', 'CREATED']
passing_df = trackingStats.get_data({'Season': year, 'PerMode': 'Totals', 'PtMeasureType': 'Passing'},
                                    override_file=data_override)[passing_cols]

merge_cols = ['PLAYER_ID', 'TEAM_ID']
merge_df = pd.merge(base_cols, advanced_cols, on=merge_cols)
merge_df = pd.merge(merge_df, passing_df, on=merge_cols)
None