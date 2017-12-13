from util.data import get_merged_shot_pbp_data, GeneralPlayerStats, get_year_string
from util.reddit import print_reddit_table
import pandas as pd

general_player_stats = GeneralPlayerStats()

df = pd.DataFrame()
for year in range(1996, 2018):
    season = get_year_string(year)

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

    general_stats_df = general_player_stats.get_data({'Season': season, 'PerMode': 'PerGame', 'MeasureType': 'Base'},
                                                     override_file=False)

    general_stats_df = general_stats_df[general_stats_df.GP >= (8 if season == '2017-18' else 40)]
    players = general_stats_df[general_stats_df.AST > 8].PLAYER_NAME

    assist_data = []
    for p in players:
        player_assist_df = shots_df[shots_df.PLAYER2_NAME == p]
        player_data = {'Player': p + ' ' + season, 'Assists': len(player_assist_df), 'Exp_Points_Per_Pot_Assist': 0,
                       'GP': len(player_assist_df.GAME_ID.unique())}

        for z in shot_zones:
            player_zone_df = player_assist_df[player_assist_df['SHOT_ZONE_BASIC'].str.contains(z)]
            zone_assists = len(player_zone_df)
            zone_pct = round(zone_assists / player_data['Assists'], 2)
            player_data[z] = zone_pct
            player_data['Exp_Points_Per_Pot_Assist'] += zone_pct * shot_zones[z]

        assist_data.append(player_data)

    assist_df = pd.DataFrame(assist_data)

    assist_df['3_pct'] = assist_df['Above the Break 3'] + assist_df['Corner 3']
    assist_df['Mid'] = assist_df['In The Paint \(Non-RA\)'] + assist_df['Mid-Range']

    assist_df['Points_Created'] = (assist_df['Assists'] * assist_df['3_pct'] * 3) + (
        (assist_df['Assists'] * (1 - assist_df['3_pct']) * 2))

    assist_df['PPG'] = assist_df['Points_Created'] / assist_df['GP']

    df = df.append(assist_df)

# df = df.sort_values(by='Exp_Points_Per_Pot_Assist', ascending=False)

print_reddit_table(df[df.Player.str.contains('Chris Paul')], ['Player', '3_pct', 'Restricted Area', 'Mid', 'Exp_Points_Per_Pot_Assist', 'PPG'])