from util.data import HustleStats, GeneralPlayerStats, TrackingStats, data_dir, file_check
import pandas as pd

file_path = data_dir + 'DefensiveRatings/data.csv'

season = '2016-17'
per_mode = 'Totals'

base = GeneralPlayerStats().get_data({'Season': season, 'PerMode': per_mode})[
    ['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'STL', 'BLK', 'MIN']]
advanced = GeneralPlayerStats().get_data({'Season': season, 'MeasureType': 'Advanced', 'PerMode': per_mode})[
    ['PLAYER_ID', 'TEAM_ID', 'PACE']]
hustle = HustleStats().get_data({'Season': season, 'PerMode': per_mode})[
    ['PLAYER_ID', 'TEAM_ID', 'LOOSE_BALLS_RECOVERED', 'DEFLECTIONS', 'CONTESTED_SHOTS_3PT']]
rebounding = TrackingStats().get_data({'Season': season, 'PtMeasureType': 'Rebounding', 'PerMode': per_mode})[
    ['PLAYER_ID', 'TEAM_ID', 'DREB_CONTEST']]
defense = TrackingStats().get_data({'Season': season, 'PtMeasureType': 'Defense', 'PerMode': per_mode})[
    ['PLAYER_ID', 'TEAM_ID', 'DEF_RIM_FGA', 'DEF_RIM_FG_PCT']]

merge_df = pd.merge(base, advanced, on=['PLAYER_ID', 'TEAM_ID'])
merge_df = merge_df.merge(hustle, on=['PLAYER_ID', 'TEAM_ID'])
merge_df = merge_df.merge(rebounding, on=['PLAYER_ID', 'TEAM_ID'])
merge_df = merge_df.merge(defense, on=['PLAYER_ID', 'TEAM_ID'])

merge_df = merge_df[merge_df.MIN >= 1000]
merge_df['POSS'] = merge_df['MIN'] * (merge_df['PACE'] / 48)

rate_stats = ['STL', 'BLK', 'LOOSE_BALLS_RECOVERED', 'DEFLECTIONS', 'CONTESTED_SHOTS_3PT', 'DREB_CONTEST',
              'DEF_RIM_FGA', 'DEF_RIM_FG_PCT']

pdr_stats = ['STL', 'LOOSE_BALLS_RECOVERED', 'DEFLECTIONS', 'CONTESTED_SHOTS_3PT']
idr_stats = ['DREB_CONTEST', 'DEF_RIM_FGA', 'DEF_RIM_FG_PCT', 'BLK']

adj_df = merge_df[['PLAYER_NAME', 'TEAM_ABBREVIATION']]
adj_df['PDR'] = 0
adj_df['IDR'] = 0

for stat in rate_stats:
    if stat is not 'DEF_RIM_FG_PCT':
        per_poss = (merge_df[stat] / merge_df['POSS']) * 100
    else:
        per_poss = merge_df[stat]
    mean = per_poss.mean()
    std = per_poss.std()
    adj = (per_poss - mean) / std
    if stat in pdr_stats:
        adj_df.PDR += adj
    if stat in idr_stats:
        adj_df.IDR += adj

adj_df['DR'] = adj_df.PDR + adj_df.IDR
adj_df = adj_df.sort_values(by='DR', ascending=False)


file_check(file_path)
adj_df.to_csv(file_path)