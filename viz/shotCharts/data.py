from util.util import merge_shot_pbp_for_season, merge_shot_pbp_for_game


def get_shot_data_for_game(game_id, season='2017-18', file_path='data.json'):
    if game_id == '':
        shots_df = merge_shot_pbp_for_season(season=season, override_file=False)
    else:
        shots_df = merge_shot_pbp_for_game(season=season, game_id=game_id)

    player_df = shots_df.rename(columns={
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

    player_df = player_df[['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'assist', 'shooter', 'quarter', 'time']]

    player_df['x'] = round(player_df['x'] / 10)
    player_df['y'] = round(player_df['y'] / 10)

    player_df.to_json(file_path, orient='records')