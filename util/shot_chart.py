from util.merge_shot_pbp import merge_shot_pbp_for_season, merge_shot_pbp_for_game
import json


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

    shots_df = shots_df[
        ['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'assist', 'shooter', 'blocker', 'quarter', 'time']]
    shots_df.loc[:, 'player'] = shots_df['shooter']

    assists_df = shots_df.loc[shots_df['assist'].notnull(), :]
    assists_df.loc[:, 'player'] = assists_df['assist']

    shots_df = shots_df.append(assists_df)

    shots_df.loc[:, 'x'] = shots_df['x'] / 10
    shots_df.loc[:, 'y'] = shots_df['y'] / 10

    return shots_df


def get_shots_for_player_season(player_name, season, override_file=False):
    shots_df = merge_shot_pbp_for_season(season=season, override_file=override_file)

    # shots_df = shots_df[shots_df['SHOT_ATTEMPTED_FLAG'].notnull()]

    shots_df = shots_df.rename(columns={
        'LOC_X': 'x', 'LOC_Y': 'y',
        'ACTION_TYPE': 'action_type',
        'SHOT_DISTANCE': 'shot_distance',
        'SHOT_MADE_FLAG': 'shot_made_flag',
        'SHOT_ATTEMPTED_FLAG': 'shot_attempted_flag',
        'SHOT_TYPE': 'shot_type',
        'SHOT_ZONE_BASIC': 'zone',
        'SHOT_ZONE_AREA': 'area',
        'PLAYER2_NAME': 'assist',
        'PLAYER1_NAME': 'shooter',
        'PLAYER3_NAME': 'blocker',
        'PERIOD': 'quarter',
        'PCTIMESTRING': 'time'
    })

    shots_df = shots_df[
        ['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'zone', 'area', 'shot_type', 'assist', 'shooter',
         'blocker', 'quarter', 'time']]
    shots_df.loc[:, 'player'] = shots_df['shooter']
    shots_df = shots_df[shots_df['shooter'] == player_name]

    shots_df.loc[:, 'x'] = shots_df['x'] / 10
    shots_df.loc[:, 'y'] = shots_df['y'] / 10

    return shots_df


def get_shots_for_all_players_season(season, override_file=False):
    shots_df = merge_shot_pbp_for_season(season=season, override_file=override_file)

    shots_df = shots_df[shots_df['SHOT_ATTEMPTED_FLAG'].notnull()]

    shots_df = shots_df.rename(columns={
        'LOC_X': 'x', 'LOC_Y': 'y',
        'ACTION_TYPE': 'action_type',
        'SHOT_DISTANCE': 'shot_distance',
        'SHOT_MADE_FLAG': 'shot_made_flag',
        'SHOT_ATTEMPTED_FLAG': 'shot_attempted_flag',
        'SHOT_TYPE': 'shot_type',
        'SHOT_ZONE_BASIC': 'zone',
        'SHOT_ZONE_AREA': 'area',
        'PLAYER2_NAME': 'assist',
        'PLAYER1_NAME': 'shooter',
        'PLAYER3_NAME': 'blocker',
        'PERIOD': 'quarter',
        'PCTIMESTRING': 'time'
    })

    shots_df = shots_df[
        ['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'shot_type', 'zone', 'area', 'assist', 'shooter',
         'blocker', 'quarter', 'time']]

    shots_df.loc[:, 'x'] = shots_df['x'] / 10
    shots_df.loc[:, 'y'] = shots_df['y'] / 10

    return shots_df


def nest_data_for_all_players_season(season, override_file=False):
    shots_df = get_shots_for_all_players_season(season, override_file=override_file)
    players = shots_df['shooter'].unique().tolist()

    shots_df['x'] = shots_df['x'].apply(lambda x: round(x))
    shots_df['y'] = shots_df['y'].apply(lambda y: round(y))

    shots_df['zone_area'] = shots_df['zone'] + ' ' + shots_df['area']

    zone_areas = shots_df['zone_area'].unique().tolist()

    league_averages = {
        'overall': {
            'pct': len(shots_df[shots_df['shot_made_flag'] == 1]) / len(shots_df),
            'efg': 0
        }
    }

    for za in zone_areas:
        za_df = shots_df[shots_df['zone_area'] == za]
        za_val = 2 if za_df.iloc[0].shot_type == '2PT Field Goal' else 3
        za_makes = len(za_df[za_df.shot_made_flag == 1])
        za_attempts = len(za_df)
        league_averages[za] = {
            'pct': za_makes / za_attempts,
            'efg': (za_makes / za_attempts) * za_val / 2,
            'val': za_val
        }
        league_averages['overall']['efg'] += za_makes * za_val

    league_averages['overall']['efg'] = league_averages['overall']['efg'] / (len(shots_df) * 2)

    x_range = range(shots_df['x'].min(), shots_df['x'].max())
    y_range = range(shots_df['y'].min(), shots_df['y'].max())

    zone_map = {}
    for x in x_range:
        zone_map[x] = {}
        for y in y_range:
            zone_map[x][y] = shots_df[(shots_df[x] == x) & (shots_df[y] == y)].iloc[0].zone_area

    shot_data = {}
    for player in players:
        player_df = shots_df[shots_df['shooter'] == player]
        if len(player_df) > 1000:
            print(player + ': ' + str(len(player_df)))
            player_xy_data = []
            uniques = player_df.groupby(['x', 'y'])
            None
            for x in player_df[x].unique():
                for y in y_range:
                    coord_df = player_df[
                        (player_df['x'] == x) &
                        (player_df['y'] == y)
                        ]
                    if len(coord_df > 0):
                        coord_data = {
                            'x': x,
                            'y': y,
                            'attempts': len(coord_df),
                            'zone': coord_df.iloc[0].zone_area
                        }
                        player_xy_data.append(coord_data)

            player_zone_data = {}
            for za in zone_areas:
                za_df = player_df[player_df['zone_area'] == za]
                za_attempts = len(za_df)
                if za_attempts > 0:
                    za_val = league_averages[za]['val']
                    za_makes = len(za_df[za_df.shot_made_flag == 1])
                    player_zone_data[za] = {
                        'pct': za_makes / za_attempts,
                        'efg': (za_makes / za_attempts) * za_val / 2
                    }
                    player_zone_data[za]['zone_rel_pct'] = player_zone_data[za]['pct'] - league_averages[za]['pct']
                    player_zone_data[za]['overall_rel_pct'] = player_zone_data[za]['efg'] - league_averages['overall'][
                        'efg']
                else:
                    player_zone_data[za] = {
                        'pct': 0,
                        'efg': 0,
                        'zone_rel_pct': 0,
                        'overall_rel_pct': 0
                    }

            shot_data[player] = {
                'xy': player_xy_data,
                'zones': player_zone_data
            }
    return shot_data


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

    blocks_df = blocks_df[
        ['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'assist', 'shooter', 'blocker', 'quarter', 'time']]

    blocks_df['player'] = player_name

    blocks_df.loc[:, 'x'] = blocks_df['x'] / 10
    blocks_df.loc[:, 'y'] = blocks_df['y'] / 10

    return blocks_df
