from util.util import merge_shot_pbp_for_season, merge_shot_pbp_for_game


def get_shot_data_for_all_players_game(game_id, season='2017-18', data_override=False):
    shots_df = merge_shot_pbp_for_game(season=season, game_id=game_id, override_file=data_override)

    shots_df = shots_df[shots_df['SHOT_ATTEMPTED_FLAG'].notnull()]

    shots_df = shots_df.rename(columns={
        'LOC_X': 'x', 'LOC_Y': 'y',
        'ACTION_TYPE': 'action_type',
        'SHOT_DISTANCE': 'shot_distance',
        'SHOT_MADE_FLAG': 'shot_made_flag',
        'SHOT_ATTEMPTED_FLAG': 'shot_attempted_flag',
        'PLAYER2_NAME': 'assist',
        'PLAYER1_NAME': 'shooter',
        'PLAYER3_NAME': 'blocker',
        'PERIOD': 'quarter',
        'PCTIMESTRING': 'time'
    })

    shots_df = shots_df[['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'assist', 'shooter', 'blocker', 'quarter', 'time']]
    shots_df.loc[:, 'player'] = shots_df['shooter']

    assists_df = shots_df.loc[shots_df['assist'].notnull(), :]
    assists_df.loc[:, 'player'] = assists_df['assist']

    shots_df = shots_df.append(assists_df)

    shots_df.loc[:, 'x'] = shots_df['x'] / 10
    shots_df.loc[:, 'y'] = shots_df['y'] / 10

    return shots_df


def get_shots_for_player_season(player_name, season, override_file='False'):
    shots_df = merge_shot_pbp_for_season(season=season, override_file=override_file)

    shots_df = shots_df[shots_df['SHOT_ATTEMPTED_FLAG'].notnull()]

    shots_df = shots_df.rename(columns={
        'LOC_X': 'x', 'LOC_Y': 'y',
        'ACTION_TYPE': 'action_type',
        'SHOT_DISTANCE': 'shot_distance',
        'SHOT_MADE_FLAG': 'shot_made_flag',
        'SHOT_ATTEMPTED_FLAG': 'shot_attempted_flag',
        'PLAYER2_NAME': 'assist',
        'PLAYER1_NAME': 'shooter',
        'PLAYER3_NAME': 'blocker',
        'PERIOD': 'quarter',
        'PCTIMESTRING': 'time'
    })

    shots_df = shots_df[
        ['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'assist', 'shooter', 'blocker', 'quarter', 'time']]
    shots_df.loc[:, 'player'] = shots_df['shooter']
    shots_df = shots_df[shots_df['shooter'] == player_name]

    assists_df = shots_df.loc[shots_df['assist'].notnull(), :]
    assists_df.loc[:, 'player'] = assists_df['assist']
    assists_df = assists_df[assists_df['assist'] == player_name]

    shots_df = shots_df.append(assists_df)

    shots_df.loc[:, 'x'] = shots_df['x'] / 10
    shots_df.loc[:, 'y'] = shots_df['y'] / 10

    return shots_df


def get_blocks_for_player_season(player_name, season, override_file='False'):
    shots_df = merge_shot_pbp_for_season(season=season, override_file=override_file)

    blocks_df = shots_df[shots_df['PLAYER3_NAME'] == player_name]

    blocks_df = blocks_df.rename(columns={
        'LOC_X': 'x', 'LOC_Y': 'y',
        'ACTION_TYPE': 'action_type',
        'SHOT_DISTANCE': 'shot_distance',
        'SHOT_MADE_FLAG': 'shot_made_flag',
        'SHOT_ATTEMPTED_FLAG': 'shot_attempted_flag',
        'PLAYER2_NAME': 'assist',
        'PLAYER1_NAME': 'shooter',
        'PLAYER3_NAME': 'blocker',
        'PERIOD': 'quarter',
        'PCTIMESTRING': 'time'
    })

    blocks_df = blocks_df[['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'assist', 'shooter', 'blocker', 'quarter', 'time']]

    blocks_df['player'] = player_name

    blocks_df.loc[:, 'x'] = blocks_df['x'] / 10
    blocks_df.loc[:, 'y'] = blocks_df['y'] / 10

    return blocks_df
