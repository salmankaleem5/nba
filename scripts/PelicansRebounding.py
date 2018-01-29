from util.data import TrackingStats, GeneralTeamStats, get_year_string
import pandas as pd

tracking_stats = TrackingStats()
general_team_stats = GeneralTeamStats()

df = pd.DataFrame()
for s in range(2017, 2018):
    season = get_year_string(s)
    tracking_reb_df = tracking_stats.get_data({'Season': season, 'PtMeasureType': 'Rebounding', 'PerMode': 'PerGame',
                                                   'PlayerOrTeam': 'Team', 'OpponentTeamID': '0'}, override_file=False)[    
            ['TEAM_ID', 'OREB_CHANCE_PCT', 'OREB_CHANCES', 'OREB', 'OREB_CHANCE_DEFER', 'OREB_CONTEST', 'OREB_UNCONTEST']]
        
    advanced_df = general_team_stats.get_data({'Season': season, 'MeasureType': 'Advanced', 'PerMode': 'PerGame'},
                                                  override_file=False)[['TEAM_ID', 'TEAM_NAME', 'OREB_PCT']]
    
    merge_df = pd.merge(tracking_reb_df, advanced_df, on='TEAM_ID')
    merge_df['YEAR'] = season
    df = df.append(merge_df)
    
df['OREB_AVAILABLE'] = df['OREB'] / df['OREB_PCT']
df['OREB_CHANCE_PER_AV'] = df['OREB_CHANCES'] / df['OREB_AVAILABLE']
df['OREB_DEFER_PER_AV'] = df['OREB_CHANCE_DEFER'] / df['OREB_AVAILABLE']

corr = df.corr()
df.to_csv('OREB.csv')

None
