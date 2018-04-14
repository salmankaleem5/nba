from util.merge_shot_pbp import merge_shot_pbp_for_season, merge_shot_pbp_for_game
from util.data_scrappers.nba_stats import GeneralPlayerStats, GeneralTeamStats


def rename_columns_for_front_end(shots_df):
    return shots_df.rename(columns={
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
        'PCTIMESTRING': 'time',
        'PLAYER1_TEAM_ABBREVIATION': 'shooting_team'
    })


def get_shot_data_for_all_players_game(pbp_df, game_id, season, data_override=False):
    shots_df = merge_shot_pbp_for_game(pbp_df, game_id, season, override_file=data_override)

    shots_df = rename_columns_for_front_end(shots_df)

    shots_df = shots_df[
        ['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'assist', 'shooter', 'blocker', 'quarter', 'time',
         'shooting_team']]
    shots_df.loc[:, 'player'] = shots_df['shooter']

    assists_df = shots_df.loc[shots_df['assist'].notnull(), :]
    assists_df.loc[:, 'player'] = assists_df['assist']

    shots_df = shots_df.append(assists_df)

    shots_df.loc[:, 'x'] = shots_df['x'] / 10
    shots_df.loc[:, 'y'] = shots_df['y'] / 10

    return shots_df


def get_shots_for_player_season(player_name, season, override_file=False):
    shots_df = merge_shot_pbp_for_season(season=season, override_file=override_file)

    shots_df = rename_columns_for_front_end(shots_df)

    shots_df = shots_df[
        ['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'zone', 'area', 'shot_type', 'assist', 'shooter',
         'blocker', 'quarter', 'time']]
    shots_df.loc[:, 'player'] = shots_df['shooter']
    shots_df = shots_df[shots_df['shooter'] == player_name]

    shots_df.loc[:, 'x'] = shots_df['x'] / 10
    shots_df.loc[:, 'y'] = shots_df['y'] / 10

    return shots_df


def get_blocks_for_player_season(player_name, season, override_file='False'):
    shots_df = merge_shot_pbp_for_season(season=season, override_file=override_file)

    blocks_df = shots_df[shots_df['PLAYER3_NAME'] == player_name]

    blocks_df = rename_columns_for_front_end(blocks_df)

    blocks_df = blocks_df[
        ['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'assist', 'shooter', 'blocker', 'quarter', 'time']]

    blocks_df['player'] = player_name

    blocks_df.loc[:, 'x'] = blocks_df['x'] / 10
    blocks_df.loc[:, 'y'] = blocks_df['y'] / 10

    return blocks_df


def get_shots_for_all_players_season(season, override_file=False):
    shots_df = merge_shot_pbp_for_season(season=season, override_file=override_file)

    shots_df['team'] = shots_df['PLAYER1_TEAM_CITY'] + ' ' + shots_df['PLAYER1_TEAM_NICKNAME']
    shots_df = rename_columns_for_front_end(shots_df)

    shots_df = shots_df[
        ['x', 'y', 'action_type', 'shot_distance', 'shot_made_flag', 'shot_type', 'zone', 'area', 'assist', 'shooter',
         'blocker', 'quarter', 'time', 'team']]

    shots_df.loc[:, 'x'] = shots_df['x'] / 10
    shots_df.loc[:, 'y'] = shots_df['y'] / 10

    return shots_df


def calculate_overall_stats(general_stats):
    general_stats['ppg'] = round((general_stats['PTS'] / general_stats['GP']) * 100) / 100

    general_stats['efg'] = round(
        (((general_stats['FGM'] - general_stats['FG3M']) * 2) + (general_stats['FG3M'] * 3)) / (
                general_stats['FGA'] * 2) * 10000) / 100

    general_stats['efg_pct'] = round((general_stats['efg'].rank() / len(general_stats)) * 10000) / 100

    return general_stats


def generate_zone_map(shots_df):
    unique_coords = shots_df[['x', 'y']].drop_duplicates()

    zone_map = {}
    for ix, uc in unique_coords.iterrows():
        str_x = str(uc.x)
        str_y = str(uc.y)
        if str_x not in zone_map:
            zone_map[str_x] = {}
        try:
            zone_map[str_x][str_y] = shots_df[
                (shots_df['x'] == uc.x) & (shots_df['y'] == uc.y)
                ]['zone_area'].value_counts().index[0]
        except IndexError:
            continue

    return zone_map


def calculate_league_averages_by_zone(shots_df, zone_areas):
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

    return league_averages


def nest_shot_data_by_xy_for_entity(entity_df, league_averages, zone_areas):
    entity_xy_data = []
    unique_coords = entity_df[['x', 'y']].drop_duplicates()
    for ix, uc in unique_coords.iterrows():
        x = uc.x
        y = uc.y

        coord_df = entity_df[
            (entity_df['x'] == x) &
            (entity_df['y'] == y)
            ]
        if len(coord_df > 0):
            coord_data = {
                'x': int(x),
                'y': int(y),
                'attempts': len(coord_df)
            }
            entity_xy_data.append(coord_data)

    entity_zone_data = {}
    for za in zone_areas:
        za_df = entity_df[entity_df['zone_area'] == za]
        za_attempts = len(za_df)
        if za_attempts > 0:
            za_val = league_averages[za]['val']
            za_makes = len(za_df[za_df.shot_made_flag == 1])
            entity_zone_data[za] = {
                'pct': za_makes / za_attempts,
                'efg': (za_makes / za_attempts) * za_val / 2,
                'attempts': za_attempts
            }
            entity_zone_data[za]['zone_rel_pct'] = entity_zone_data[za]['pct'] - league_averages[za]['pct']
            entity_zone_data[za]['overall_rel_efg'] = entity_zone_data[za]['efg'] - league_averages['overall'][
                'efg']
        else:
            entity_zone_data[za] = {
                'pct': 0,
                'efg': 0,
                'zone_rel_pct': 0,
                'overall_rel_pct': 0
            }

    return {
        'xy': entity_xy_data,
        'zones': entity_zone_data,
    }


def nest_data_for_all_players_season(season, fga_filter=500, override_file=False):
    shots_df = get_shots_for_all_players_season(season, override_file=override_file)
    shots_df['zone_area'] = shots_df['zone'] + ' ' + shots_df['area']

    general_stats = GeneralPlayerStats().get_data({'Season': season, 'PerMode': 'Totals'}, override_file=override_file)
    general_stats = general_stats[general_stats['FGA'] >= fga_filter]
    general_stats = calculate_overall_stats(general_stats)

    general_stats = general_stats[['PLAYER_NAME', 'ppg', 'efg', 'efg_pct']]

    players = general_stats['PLAYER_NAME'].unique().tolist()

    general_stats = general_stats.set_index('PLAYER_NAME').T.to_dict()

    shots_df['x'] = shots_df['x'].apply(lambda lx: round(lx))
    shots_df['y'] = shots_df['y'].apply(lambda ly: round(ly))

    zone_areas = shots_df['zone_area'].unique().tolist()

    league_averages = calculate_league_averages_by_zone(shots_df, zone_areas)

    zone_map = generate_zone_map(shots_df)

    shot_data = {'zone_map': zone_map, 'players': {}}
    for player in players:
        player_df = shots_df[shots_df['shooter'] == player]
        print(player + ': ' + str(len(player_df)))

        shot_data['players'][player] = nest_shot_data_by_xy_for_entity(player_df, league_averages, zone_areas)
        shot_data['players'][player]['stats'] = general_stats[player]

    return shot_data


def nest_data_for_teams_season(season, override_file=False):
    shots_df = get_shots_for_all_players_season(season, override_file=override_file)
    shots_df['zone_area'] = shots_df['zone'] + ' ' + shots_df['area']

    general_stats = GeneralTeamStats().get_data({'Season': season, 'PerMode': 'Totals'}, override_file=override_file)
    general_stats = calculate_overall_stats(general_stats)

    teams = shots_df['team'].unique().tolist()

    general_stats = general_stats[['TEAM_NAME', 'ppg', 'efg', 'efg_pct']]

    general_stats = general_stats.set_index('TEAM_NAME').T.to_dict()

    shots_df['x'] = shots_df['x'].apply(lambda lx: round(lx))
    shots_df['y'] = shots_df['y'].apply(lambda ly: round(ly))

    zone_areas = shots_df['zone_area'].unique().tolist()

    league_averages = calculate_league_averages_by_zone(shots_df, zone_areas)

    zone_map = generate_zone_map(shots_df)

    shot_data = {'zone_map': zone_map, 'teams': {}}
    for team in teams:
        team_df = shots_df[shots_df['shooter'] == team]
        print(team + ': ' + str(len(team_df)))

        shot_data['teams'][team] = nest_shot_data_by_xy_for_entity(team_df, league_averages, zone_areas)
        shot_data['teams'][team]['stats'] = general_stats[team]

    return shot_data
