from util.util import merge_shot_pbp_for_season, merge_shot_pbp_for_game


def update_file_to_player(player_name, season='2017-18', game_id=''):
    if game_id == '':
        shots_df = merge_shot_pbp_for_season(season=season, override_file=False)
    else:
        shots_df = merge_shot_pbp_for_game(season=season, game_id=game_id)

    player_df = shots_df[shots_df['PLAYER1_NAME'] == player_name]

    player_df = player_df.rename(columns={
        'LOC_X': 'x', 'LOC_Y': 'y',
        'ACTION_TYPE': 'action_type',
        'SHOT_DISTANCE': 'shot_distance',
        'SHOT_MADE_FLAG': 'shot_made_flag',
        'SHOT_ATTEMPTED_FLAG': 'shot_attempted_flag',
        'PLAYER2_NAME': 'assist'
    })

    player_df['x'] = round(player_df['x'] / 10)
    player_df['y'] = round(player_df['y'] / 10)

    player_df.to_json('data.json', orient='records')


update_file_to_player('Anthony Davis', season='2017-18', game_id='0021700635')
