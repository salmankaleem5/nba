from util.data import TrackingStats, GeneralPlayerStats, ShotTracking, get_merged_shot_pbp_data
import pandas as pd

season = '2017-18'
per_mode = 'Totals'
data_refresh = True

tracking_endpoint = TrackingStats()
general_endpoint = GeneralPlayerStats()
shot_tracking_endpoint = ShotTracking()


def calculate_points(shot_df):
    return len(shot_df[shot_df.SHOT_TYPE == '2PT Field Goal']) * 2 + len(
        shot_df[shot_df.SHOT_TYPE == '3PT Field Goal']) * 3


def calculate_points_added_by_assists():
    # For all player we want to calculate the efg on shots which they potential assist and shots which they do not
    # efg potential assisted shots = points created by assists / potential assists
    # efg non-assisted shots = teammate points which player did not assist / shots on which on a player did not assist

    shot_pbp_df = get_merged_shot_pbp_data(season)
    df = tracking_endpoint.get_data({'Season': season, 'PerMode': per_mode, 'PtMeasureType': 'Passing'},
                                    override_file=data_refresh)[
        ['PLAYER_NAME', 'GP', 'TEAM_ABBREVIATION', 'POTENTIAL_AST']]

    assist_point_data = []
    players = df.PLAYER_NAME.tolist()
    for p in players:
        player_data = {'PLAYER_NAME': p}

        # Create df of all shots the player assisted, separate 2 and 3's to calculate total points on assisted shots
        # By definition an assisted shot is made
        player_assist_df = shot_pbp_df[shot_pbp_df.PLAYER2_NAME == p]
        player_data['AST_PTS'] = calculate_points(player_assist_df)

        # Get the players team, filter for players with that team abbreviation, and remove the current player to
        # get a list of player teammates. Filter shot df for those players
        player_team = df[df.PLAYER_NAME == p].iloc[0].TEAM_ABBREVIATION
        player_teammates = df[df.TEAM_ABBREVIATION == player_team]
        player_teammates = player_teammates[player_teammates.PLAYER_NAME != p].PLAYER_NAME.tolist()
        player_teammate_shots = shot_pbp_df[shot_pbp_df.PLAYER1_NAME.isin(player_teammates)]

        # Number of unassisted teammate shots will be total teammate shots (length of teammate shot df) - a player's
        # potential assists.
        unassisted_teammate_fga = len(player_teammate_shots) - df[df.PLAYER_NAME == p].iloc[0].POTENTIAL_AST

        # Remove the shots a player assisted. We need to keep the players assisted shots in the teammate shot df for
        # the unassisted teammate fga calculation since we are already subtracted potential assists (removing the
        # assisted shots would double count). Calculate makes with the shot made flag after removing assisted shots.
        player_teammate_shots = player_teammate_shots[player_teammate_shots.PLAYER2_NAME != p]
        player_teammates_makes = player_teammate_shots[player_teammate_shots.SHOT_MADE_FLAG == 1]

        # Calculate teammate unassisted points the same was as assist points
        player_teammate_unassisted_points = calculate_points(player_teammates_makes)

        # Using unassisted points and attempts we can calculate an unassisted efg
        player_data['UNAST_EFG'] = (player_teammate_unassisted_points / unassisted_teammate_fga) / 2

        assist_point_data.append(player_data)

    df = df.merge(pd.DataFrame(assist_point_data), on='PLAYER_NAME', how='inner')
    df['AST_EFG'] = (df['AST_PTS'] / df['POTENTIAL_AST']) / 2
    df['ADDED_AST_EFG'] = df['AST_EFG'] - df['UNAST_EFG']
    df['AST_PTS'] = df['ADDED_AST_EFG'] * df['POTENTIAL_AST']
    df['AST_PTS_PER_GP'] = df['AST_PTS'] / df['GP']
    df = df[df.POTENTIAL_AST >= 50]
    df = df.sort_values(by='AST_PTS_PER_GP', ascending=False)
    return df[['PLAYER_NAME', 'POTENTIAL_AST', 'ADDED_AST_EFG', 'AST_PTS', 'AST_PTS_PER_GP']]


def calculate_points_received_from_assists():
    # Potential Assists are defined as shots which occur within 1 dribble of receiving the ball. Points received
    # from assists will be defined by the difference between a players' percentage on 0 and 1 dribble shots
    # compared to their percentages on >=2 dribble shots
    assisted_types = ['0 Dribbles', '1 Dribble']
    unassisted_types = ['2 Dribbles', '3-6 Dribbles', '7+ Dribbles']

    unassisted_df = pd.DataFrame(columns=['PLAYER_NAME'])
    for t in unassisted_types:
        shooting_df = shot_tracking_endpoint.get_data({'Season': season, 'PerMode': per_mode, 'DribbleRange': t},
                                                      override_file=data_refresh)[['PLAYER_NAME', 'FGA', 'EFG_PCT']]
        shooting_df.columns = ['PLAYER_NAME', t + '_FGA', t + '_EFG']
        unassisted_df = unassisted_df.merge(shooting_df, on='PLAYER_NAME', how='outer')
    unassisted_df = unassisted_df.fillna(0)

    assisted_df = pd.DataFrame(columns=['PLAYER_NAME'])
    for t in assisted_types:
        shooting_df = shot_tracking_endpoint.get_data({'Season': season, 'PerMode': per_mode, 'DribbleRange': t},
                                                      override_file=data_refresh)[['PLAYER_NAME', 'FGA', 'EFG_PCT']]
        shooting_df.columns = ['PLAYER_NAME', t + '_FGA', t + '_EFG']
        assisted_df = assisted_df.merge(shooting_df, on='PLAYER_NAME', how='outer')
    assisted_df = assisted_df.fillna(0)

    unassisted_df['UNAST_PTS'] = 0
    unassisted_df['UNAST_FGA'] = 0
    for t in unassisted_types:
        unassisted_df['UNAST_FGA'] += unassisted_df[t + '_FGA']
        unassisted_df['UNAST_PTS'] += unassisted_df[t + '_FGA'] * unassisted_df[t + '_EFG']
    unassisted_df['UNAST_EFG'] = unassisted_df['UNAST_PTS'] / unassisted_df['UNAST_FGA']

    assisted_df['AST_PTS'] = 0
    assisted_df['AST_FGA'] = 0
    for t in assisted_types:
        assisted_df['AST_FGA'] += assisted_df[t + '_FGA']
        assisted_df['AST_PTS'] += assisted_df[t + '_FGA'] * assisted_df[t + '_EFG']
    assisted_df['AST_EFG'] = assisted_df['AST_PTS'] / assisted_df['AST_FGA']

    unassisted_df = unassisted_df[['PLAYER_NAME', 'UNAST_FGA', 'UNAST_EFG', 'UNAST_PTS']]
    assisted_df = assisted_df[['PLAYER_NAME', 'AST_FGA', 'AST_EFG', 'AST_PTS']]

    df = pd.merge(assisted_df, unassisted_df, on='PLAYER_NAME', how='outer')

    df['TOTAL_FGA'] = df['UNAST_FGA'] + df['AST_FGA']
    df['TOTAL_PTS'] = (df['UNAST_FGA'] * df['UNAST_EFG']) + (df['AST_FGA'] * df['AST_EFG'])
    df['ACTUAL_EFG'] = df['TOTAL_PTS'] / df['TOTAL_FGA']
    df['ADJ_PTS'] = df['TOTAL_FGA'] * df['UNAST_EFG']
    df['ADJ_EFG'] = df['ADJ_PTS'] / df['TOTAL_FGA']

    average_unast_efg = df['UNAST_PTS'].sum() / df['UNAST_FGA'].sum()
    df['ADDED_PTS_EFG'] = df['UNAST_EFG'] - average_unast_efg
    df['PTS_VAL'] = df['ADDED_PTS_EFG'] * df['TOTAL_FGA']

    df = df.sort_values(by='TOTAL_PTS', ascending=False)
    df = df[df.UNAST_FGA >= 50]
    return df[['PLAYER_NAME', 'TOTAL_PTS', 'ACTUAL_EFG', 'ADJ_PTS', 'ADJ_EFG', 'ADDED_PTS_EFG', 'PTS_VAL', 'TOTAL_FGA']]


passing_df = calculate_points_added_by_assists()
scoring_df = calculate_points_received_from_assists()
merge_df = pd.merge(passing_df, scoring_df, on=['PLAYER_NAME'], how='outer').fillna(0)
merge_df['TOTAL_VAL'] = merge_df['AST_VAL'] + merge_df['PTS_VAL']

general_stats = general_endpoint.get_data({'Season': season, 'PerMode': per_mode, 'MeasureType': 'Base'},
                                          override_file=data_refresh)
general_stats = general_stats[['PLAYER_NAME', 'FTM', 'GP']]
merge_df = merge_df.merge(general_stats, on='PLAYER_NAME')

merge_df['POINTS_SCORED'] = merge_df['ADJ_PTS'] + merge_df['FTM']
merge_df['POINTS_ASSISTED'] = merge_df['AST_VAL']
merge_df['TOTAL_POINTS_CREATED'] = merge_df['POINTS_SCORED'] + merge_df['POINTS_ASSISTED']
total_poss = merge_df['POTENTIAL_AST'] + merge_df['TOTAL_FGA']
merge_df['RELATIVE_EFG'] = (merge_df['ADDED_AST_EFG'] * (merge_df['POTENTIAL_AST'] / total_poss)) + (
    merge_df['ADDED_PTS_EFG'] * (merge_df['TOTAL_FGA'] / total_poss))
merge_df['RELATIVE_TS'] = merge_df['TOTAL_POINTS_CREATED'] / (total_poss + 0.44 * merge_df['FTM'])

final_df = merge_df[['PLAYER_NAME', 'GP', 'POINTS_SCORED', 'POINTS_ASSISTED', 'TOTAL_POINTS_CREATED', 'RELATIVE_EFG']]

final_df['POINTS_SCORED'] = final_df['POINTS_SCORED'] / final_df['GP']
final_df['POINTS_ASSISTED'] = final_df['POINTS_ASSISTED'] / final_df['GP']
final_df['TOTAL_POINTS_CREATED'] = final_df['TOTAL_POINTS_CREATED'] / final_df['GP']
final_df['REPLATIVE_EFG'] = final_df['RELATIVE_EFG'] * 100

final_df = final_df.sort_values(by='TOTAL_POINTS_CREATED', ascending=False)
None
