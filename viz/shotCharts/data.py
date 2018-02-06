from util.util import merge_shot_pbp_for_game


def get_shot_data_for_game(game_id, season='2017-18', file_path='data.json', data_override=False):
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
        'PERIOD': 'quarter',
        'PCTIMESTRING': 'time'
    })

    shots_df = shots_df[['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'assist', 'shooter', 'quarter', 'time']]
    shots_df['player'] = shots_df['shooter']

    assists_df = shots_df[shots_df['assist'].notnull()]
    assists_df['player'] = assists_df['assist']

    shots_df = shots_df.append(assists_df)

    shots_df['x'] = shots_df['x'] / 10
    shots_df['y'] = shots_df['y'] / 10

    shots_df.to_json(file_path, orient='records')