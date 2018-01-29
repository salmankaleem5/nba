from util.data import get_merged_shot_pbp_data, GeneralPlayerStats, get_year_string, TrackingStats
from util.reddit import print_reddit_table
import pandas as pd

general_player_ep = GeneralPlayerStats()
tracking_ep = TrackingStats()
data_override = False
season_range = (2017, 2017)
games_filter = 20
assist_filter = 4

df = pd.DataFrame()
for year in [2017]:
    season = get_year_string(year)
    print(season)

    shots_df = get_merged_shot_pbp_data(season)
    shot_zones = {
        'Above the Break 3': 0,
        'Corner 3': 0,
        'Mid-Range': 0,
        'In The Paint \(Non-RA\)': 0,
        'Restricted Area': 0
    }
    for z in shot_zones:
        zone_df = shots_df[shots_df['SHOT_ZONE_BASIC'].str.contains(z)]
        fga = len(zone_df)
        fgm = zone_df.SHOT_MADE_FLAG.sum()
        val = 3 if '3' in z else 2
        points = fgm * val
        shot_zones[z] = round(points / fga, 2)

    print(shot_zones)

    general_stats_df = general_player_ep.get_data({'Season': season, 'PerMode': 'PerGame', 'MeasureType': 'Base'},
                                                  override_file=data_override)
    tracking_stats_df = tracking_ep.get_data({'Season': season, 'PerMode': 'Totals', 'PtMeasureType': 'Passing'},
                                             override_file=data_override)[['PLAYER_NAME', 'POTENTIAL_AST']]

    general_stats_df = general_stats_df[general_stats_df.GP >= games_filter]
    players = general_stats_df[general_stats_df.AST > assist_filter].PLAYER_NAME

    assist_data = []
    for p in players:
        player_assist_df = shots_df[shots_df.PLAYER2_NAME == p]
        player_data = {'Player': p,
                       'Year': season,
                       'Assists': len(player_assist_df),
                       'Exp_Pts_Per_Past': 0,
                       'GP': len(player_assist_df.GAME_ID.unique())
                       }

        for z in shot_zones:
            player_zone_df = player_assist_df[player_assist_df['SHOT_ZONE_BASIC'].str.contains(z)]
            zone_assists = len(player_zone_df)
            zone_pct = round(zone_assists / player_data['Assists'], 2)
            player_data[z] = zone_pct
            player_data['Exp_Pts_Per_Past'] += zone_pct * shot_zones[z]

        assist_data.append(player_data)

    assist_df = pd.DataFrame(assist_data)

    assist_df['3_pct'] = assist_df['Above the Break 3'] + assist_df['Corner 3']
    assist_df['Mid'] = assist_df['In The Paint \(Non-RA\)'] + assist_df['Mid-Range']

    assist_df['Points_Created'] = (assist_df['Assists'] * assist_df['3_pct'] * 3) + (
        (assist_df['Assists'] * (1 - assist_df['3_pct']) * 2))

    assist_df['PPG'] = assist_df['Points_Created'] / assist_df['GP']

    assist_df = assist_df.merge(tracking_stats_df, left_on='Player', right_on='PLAYER_NAME', how='inner')

    assist_df['Pts_Per_Past'] = assist_df['Points_Created'] / assist_df['POTENTIAL_AST']
    assist_df['Diff'] = assist_df['Pts_Per_Past'] - assist_df['Exp_Pts_Per_Past']

    assist_df['Ast_pct'] = assist_df['Assists'] / assist_df['POTENTIAL_AST']

    df = df.append(assist_df)

df = df.sort_values(by='Diff', ascending=False)

df.to_csv('Passing.csv')

print_reddit_table(df, ['Player', 'POTENTIAL_AST', 'Assists', 'Ast_pct', 'Corner 3', 'Above the Break 3', 'Restricted Area', 'Mid', 'Exp_Pts_Per_Past', 'Pts_Per_Past', 'Diff'])
