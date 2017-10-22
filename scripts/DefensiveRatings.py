from util.data import HustleStats, GeneralPlayerStats, TrackingStats, data_dir, file_check
import pandas as pd


file_path = data_dir + 'DefensiveRatings/data.csv'

season = '2016-17'
per_mode = 'Totals'


rapm = pd.read_csv(data_dir + 'DefensiveRatings\\RAPM.csv')
base = GeneralPlayerStats().get_data({'Season': season, 'PerMode': per_mode})[
    ['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'STL', 'BLK', 'MIN']]
advanced = GeneralPlayerStats().get_data({'Season': season, 'MeasureType': 'Advanced', 'PerMode': per_mode})[
    ['PLAYER_ID', 'TEAM_ID', 'PACE', 'DEF_RATING']]
hustle = HustleStats().get_data({'Season': season, 'PerMode': per_mode})[
    ['PLAYER_ID', 'TEAM_ID', 'LOOSE_BALLS_RECOVERED', 'DEFLECTIONS', 'CONTESTED_SHOTS_3PT', 'CHARGES_DRAWN']]
rebounding = TrackingStats().get_data({'Season': season, 'PtMeasureType': 'Rebounding', 'PerMode': per_mode})[
    ['PLAYER_ID', 'TEAM_ID', 'DREB_CONTEST']]
defense = TrackingStats().get_data({'Season': season, 'PtMeasureType': 'Defense', 'PerMode': per_mode})[
    ['PLAYER_ID', 'TEAM_ID', 'DEF_RIM_FGA', 'DEF_RIM_FGM', 'DEF_RIM_FG_PCT']]

average_rim_pct = defense.DEF_RIM_FGM.sum() / defense.DEF_RIM_FGA.sum()
defense['POINTS_SAVED'] = (average_rim_pct - defense.DEF_RIM_FG_PCT) * defense.DEF_RIM_FGA

merge_df = pd.merge(base, advanced, on=['PLAYER_ID', 'TEAM_ID'])
merge_df = merge_df.merge(hustle, on=['PLAYER_ID', 'TEAM_ID'])
merge_df = merge_df.merge(rebounding, on=['PLAYER_ID', 'TEAM_ID'])
merge_df = merge_df.merge(defense, on=['PLAYER_ID', 'TEAM_ID'])

merge_df = merge_df.merge(rapm, on=['PLAYER_NAME'])

merge_df = merge_df.sort_v
merge_df['POSS'] = merge_df['MIN'] * (merge_df['PACE'] / 48)

rate_stats = ['STL', 'BLK', 'LOOSE_BALLS_RECOVERED', 'DEFLECTIONS', 'CONTESTED_SHOTS_3PT', 'DREB_CONTEST',
              'POINTS_SAVED', 'CHARGES_DRAWN', 'DEF_RATING']

pdr_stats = {'LOOSE_BALLS_RECOVERED': 1/3, 'DEFLECTIONS': 1/3, 'CONTESTED_SHOTS_3PT': 1/3}
idr_stats = {'DREB_CONTEST': 3/10, 'POINTS_SAVED': 6/10, 'CHARGES_DRAWN': 1/10}

adj_df = merge_df[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'MIN', 'DRAPM', 'DEF_RATING']]
adj_df['PDR'] = 0
adj_df['IDR'] = 0
adj_df['DR'] = 0

for stat in rate_stats:
    adj_df[stat + '_rate'] = (merge_df[stat] / merge_df['POSS']) * 100
    mean = adj_df[stat + '_rate'].mean()
    std = adj_df[stat + '_rate'].std()
    adj = (adj_df[stat + '_rate'] - mean) / std
    adj_df[stat + '_std_from_mean'] = adj
    if stat in pdr_stats:
        adj_df.PDR += adj * pdr_stats[stat]
    if stat in idr_stats:
        adj_df.IDR += adj * idr_stats[stat]

adj_df.DR = adj_df.PDR + adj_df.IDR
adj_df = adj_df.sort_values(by='DR', ascending=False)

file_check(file_path)
adj_df.to_csv(file_path)
