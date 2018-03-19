from util.nba_stats import GeneralPlayerStats, TrackingStats
from util.util import merge_shot_pbp_for_season
from util.format import get_year_string
from util.reddit import print_reddit_table
import pandas as pd

general_player_ep = GeneralPlayerStats()
tracking_ep = TrackingStats()


def get_stats_for_player_season(season, games_filter=50, assist_filter=5, override_file=False):
    shots_df = merge_shot_pbp_for_season(season, override_file=override_file)

    # Calculate average efficiency from each zone of the court
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

    # Get list of players meeting filter requirements
    general_stats_df = general_player_ep.get_data({
        'Season': season,
        'PerMode': 'PerGame',
        'MeasureType': 'Base'
    }, override_file=override_file)

    general_stats_df = general_stats_df[
        (general_stats_df.GP >= games_filter) &
        (general_stats_df.AST > assist_filter)
    ]
    players = general_stats_df.PLAYER_NAME.tolist()

    # For each player filter shots for ones they assisted and calculate what percentage comes from each zone
    # Use those percentages with average efficiencies to calculate expected points produced per potential assist
    assist_data = []
    for p in players:
        player_assist_df = shots_df[shots_df.PLAYER2_NAME == p]
        player_data = {
            'PLAYER_NAME': p,
            'YEAR': season,
            'AST': len(player_assist_df),
            'EXP_PTS_PER_PAST': 0,
            'GP': general_stats_df[general_stats_df['PLAYER_NAME'] == p].iloc[0]['GP']
        }

        if player_data['AST'] > 0:
            for z in shot_zones:
                player_zone_df = player_assist_df[player_assist_df['SHOT_ZONE_BASIC'].str.contains(z)]
                zone_assists = len(player_zone_df)
                zone_pct = round(zone_assists / player_data['AST'], 4)
                player_data[z] = zone_pct * 100
                player_data['EXP_PTS_PER_PAST'] += zone_pct * shot_zones[z]

            assist_data.append(player_data)

    assist_df = pd.DataFrame(assist_data)

    # PCT_3 used for calculating total Points created
    # PCT_MID calculated since paint non-ra and mid range shots give similar efficiencies
    assist_df['PCT_3'] = assist_df['Above the Break 3'] + assist_df['Corner 3']
    assist_df['PCT_MID'] = assist_df['In The Paint \(Non-RA\)'] + assist_df['Mid-Range']

    assist_df = assist_df.rename(columns={
        'Above the Break 3': 'BREAK_3',
        'Corner 3': 'CORNER_3',
        'Restricted Area': 'RESTRICTED_AREA',
        'Mid-Range': 'MID_RANGE',
        'In The Paint \(Non-RA\)': 'PAINT_NON-RA'
    })

    assist_df['AST_PTS'] = round((assist_df['AST'] * assist_df['PCT_3'] / 100 * 3) + (
        (assist_df['AST'] * (1 - assist_df['PCT_3'] / 100) * 2)), 0)

    # Add tracking data to determine actual points produced per potential assist
    # tracking_df = tracking_ep.get_data({
    #     'Season': season,
    #     'PerMode': 'Totals',
    #     'PtMeasureType': 'Passing'
    # }, override_file=override_file)[['PLAYER_NAME', 'POTENTIAL_AST']]
    #
    # assist_df = assist_df.merge(tracking_df, on='PLAYER_NAME', how='inner')
    #
    # assist_df['PTS_PER_PAST'] = assist_df['AST_PTS'] / assist_df['POTENTIAL_AST']
    # assist_df['PTS_PER_PAST_DIFF'] = assist_df['PTS_PER_PAST'] - assist_df['EXP_PTS_PER_PAST']
    #
    # assist_df = assist_df.sort_values(by='PTS_PER_PAST', ascending=False)

    return assist_df


def get_stats_for_player_year_range(year_range):
    assist_df = pd.DataFrame()
    for year in year_range:
        season = get_year_string(year)
        assist_df = assist_df.append(
            get_stats_for_player_season(
                season,
                assist_filter=4,
                override_file=False
            )
        )
        assist_df = assist_df.sort_values(by='EXP_PTS_PER_PAST', ascending=False)
    return assist_df


def get_stats_for_team_season(season, override_file=False):
    shots_df = merge_shot_pbp_for_season(season, override_file=override_file)

    # Calculate average efficiency from each zone of the court
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

    # Get list of teams
    teams = shots_df['PLAYER2_TEAM_ABBREVIATION'].unique()

    # For each team filter shots for ones they assisted and calculate what percentage comes from each zone
    # Use those percentages with average efficiencies to calculate expected points produced per potential assist
    assist_data = []
    for t in teams:
        team_assist_df = shots_df[shots_df.PLAYER2_TEAM_ABBREVIATION == t]
        if len(team_assist_df) == 0:
            continue
        team_data = {
            'TEAM_ABBREVIATION': t,
            'YEAR': season,
            'AST': len(team_assist_df),
            'EXP_PTS_PER_PAST': 0,
            'GP': len(team_assist_df.GAME_ID.unique())
        }

        for z in shot_zones:
            team_zone_df = team_assist_df[team_assist_df['SHOT_ZONE_BASIC'].str.contains(z)]
            zone_assists = len(team_zone_df)
            zone_pct = round(zone_assists / team_data['AST'], 2)
            team_data[z] = zone_pct
            team_data['EXP_PTS_PER_PAST'] += zone_pct * shot_zones[z]

        assist_data.append(team_data)

    assist_df = pd.DataFrame(assist_data)

    # PCT_3 used for calculating total Points created
    # PCT_MID calculated since paint non-ra and mid range shots give similar efficiencies
    assist_df['PCT_3'] = assist_df['Above the Break 3'] + assist_df['Corner 3']
    assist_df['PCT_MID'] = assist_df['In The Paint \(Non-RA\)'] + assist_df['Mid-Range']

    assist_df = assist_df.rename(columns={
        'Above the Break 3': 'BREAK_3',
        'Corner 3': 'CORNER_3',
        'Restricted Area': 'RESTRICTED_AREA',
        'Mid-Range': 'MID_RANGE',
        'In The Paint \(Non-RA\)': 'PAINT_NON-RA'
    })

    assist_df['AST_PTS'] = (assist_df['AST'] * assist_df['PCT_3'] * 3) + (
        (assist_df['AST'] * (1 - assist_df['PCT_3']) * 2))

    # Add tracking data to determine actual points produced per potential assist
    tracking_df = tracking_ep.get_data({
        'Season': season,
        'PerMode': 'Totals',
        'PtMeasureType': 'Passing',
        'PlayerOrTeam': 'Team'
    }, override_file=override_file)[['TEAM_ABBREVIATION', 'POTENTIAL_AST']]

    assist_df = assist_df.merge(tracking_df, on='TEAM_ABBREVIATION', how='inner')

    assist_df['PTS_PER_PAST'] = assist_df['AST_PTS'] / assist_df['POTENTIAL_AST']
    assist_df['PTS_PER_PAST_DIFF'] = assist_df['PTS_PER_PAST'] - assist_df['EXP_PTS_PER_PAST']

    assist_df = assist_df.sort_values(by='PTS_PER_PAST', ascending=False)

    assist_df = assist_df.merge(tracking_df, left_on='Player', right_on='PLAYER_NAME', how='inner')

    assist_df['Pts_Per_Past'] = assist_df['Points_Created'] / assist_df['POTENTIAL_AST']
    assist_df['Diff'] = assist_df['Pts_Per_Past'] - assist_df['Exp_Pts_Per_Past']

    assist_df['Ast_pct'] = assist_df['Assists'] / assist_df['POTENTIAL_AST']

    assist_df = assist_df.sort_values(by='Diff', ascending=False)

    print_reddit_table(assist_df, ['Player', 'POTENTIAL_AST', 'Assists', 'Ast_pct', 'Corner 3', 'Above the Break 3',
                                   'Restricted Area', 'Mid', 'Exp_Pts_Per_Past', 'Pts_Per_Past', 'Diff'])
    return assist_df


def get_stats_for_team_year_range(year_range):
    assist_df = pd.DataFrame()
    for year in year_range:
        season = get_year_string(year)
        assist_df = assist_df.append(get_stats_for_team_season(season))
        assist_df = assist_df.sort_values(by='PTS_PER_PAST', ascending=False)
    return assist_df


# xdf = get_stats_for_player_season('2017-18', override_file=True)
xdf = get_stats_for_player_year_range(range(1996, 2018))
xdf.to_csv('assist.csv')
xdf['APG'] = xdf['AST'] / xdf['GP']
xdf['PTS_PER_AST'] = xdf['AST_PTS'] / xdf['AST']
xdf = xdf.sort_values(by='RESTRICTED_AREA', ascending=False).head(50)
print_reddit_table(xdf, ['PLAYER_NAME', 'YEAR', 'GP', 'AST', 'APG', 'RESTRICTED_AREA', 'PCT_MID', 'PCT_3', 'PTS_PER_AST', 'EXP_PTS_PER_PAST'])
None
