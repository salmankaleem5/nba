from viz.rotations.data import get_rotation_data_for_game, is_home
from viz.shotCharts.data import get_shot_data_for_game
from util.util import merge_shot_pbp_for_game
from util.nba_stats import TrackingStats, HustleStats, GeneralPlayerStats
import pandas as pd
import requests
import shutil

file_dir = './data/'


def get_team_logos():
    teams = GeneralPlayerStats().get_data({})['TEAM_ABBREVIATION'].unique()
    logo_url = 'http://stats.nba.com/media/img/teams/logos/{}_logo.svg'
    logo_file_location = './img/{}.svg'
    for t in teams:
        team_logo_url = logo_url.format(t)
        team_logo_file_location = logo_file_location.format(t)
        response = requests.get(team_logo_url, stream=True)
        with open(team_logo_file_location, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response


def get_scoring_stats_from_pbp(pbp_df):
    players = pbp_df['PLAYER1_NAME'].unique()[1:]

    player_data = []
    for p in players:
        p_df = pbp_df[pbp_df['PLAYER1_NAME'] == p]

        desc = 'HOMEDESCRIPTION' if is_home(p_df, p_df['PLAYER1_TEAM_ABBREVIATION'].iloc[0]) else 'VISITORDESCRIPTION'

        ft_df = p_df[p_df['EVENTMSGTYPE'] == 3]
        ft1a = len(ft_df[ft_df[desc].str.contains('of 1')])
        ft2a = len(ft_df[ft_df[desc].str.contains('of 2')])
        ft3a = len(ft_df[ft_df[desc].str.contains('of 3')])
        ftm = len(ft_df[ft_df[desc].str.contains('PTS')])

        fg2_df = p_df[p_df['SHOT_TYPE'] == '2PT Field Goal']
        fg2a = len(fg2_df)
        fg2m = len(fg2_df[fg2_df['SHOT_MADE_FLAG'] == 1])

        fg3_df = p_df[p_df['SHOT_TYPE'] == '3PT Field Goal']
        fg3a = len(fg3_df)
        fg3m = len(fg3_df[fg3_df['SHOT_MADE_FLAG'] == 1])

        pts = (3 * fg3m) + (2 * fg2m) + ftm
        tsa = (ft2a / 2) + (ft3a / 3) + fg2a + fg3a
        eff = pts / (2 * tsa) if tsa != 0 else 0

        p_data = {
            'player': p,
            'and_one': ft1a,
            '2pt_ft': ft2a,
            '3pt_ft': ft3a,
            'ftm': ftm,
            '2pt_fga': fg2a,
            '2pt_fgm': fg2m,
            '3pt_fga': fg3a,
            '3pt_fgm': fg3m,
            'pts': pts,
            'tsa': tsa,
            'eff': round(eff * 100, 2)
        }
        player_data.append(p_data)

    return pd.DataFrame(player_data)


def get_tracking_stats_for_date(game_date, year):
    tracking_ep = TrackingStats()

    passing_df = tracking_ep.get_data({
        'PtMeasureType': 'Passing',
        'DateFrom': game_date,
        'DateTo': game_date,
        'Season': year
    })[['PLAYER_NAME', 'POTENTIAL_AST', 'PASSES_MADE', 'AST', 'AST_POINTS_CREATED']]

    possession_df = tracking_ep.get_data({
        'PtMeasureType': 'Possessions',
        'DateFrom': game_date,
        'DateTo': game_date,
        'Season': year
    })[['PLAYER_NAME', 'FRONT_CT_TOUCHES', 'TIME_OF_POSS', 'ELBOW_TOUCHES', 'POST_TOUCHES', 'PAINT_TOUCHES']]

    rebounding_df = tracking_ep.get_data({
        'PtMeasureType': 'Rebounding',
        'DateFrom': game_date,
        'DateTo': game_date,
        'Season': year
    })[['PLAYER_NAME', 'OREB', 'OREB_CHANCES', 'OREB_CHANCE_DEFER', 'OREB_CHANCE_PCT_ADJ', 'DREB', 'DREB_CHANCES',
        'DREB_CHANCE_DEFER', 'DREB_CHANCE_PCT_ADJ', 'REB', 'REB_CHANCES', 'REB_CHANCE_DEFER', 'REB_CHANCE_PCT_ADJ']]

    rebounding_df['OREB_CHANCE_PCT_ADJ'] = rebounding_df['OREB_CHANCE_PCT_ADJ'] * 100
    rebounding_df['DREB_CHANCE_PCT_ADJ'] = rebounding_df['DREB_CHANCE_PCT_ADJ'] * 100

    defense_df = tracking_ep.get_data({
        'PtMeasureType': 'Defense',
        'DateFrom': game_date,
        'DateTo': game_date,
        'Season': year
    })[['PLAYER_NAME', 'BLK', 'STL', 'DEF_RIM_FGM', 'DEF_RIM_FGA', 'DEF_RIM_FG_PCT']]

    defense_df['DEF_RIM_FG_PCT'] = defense_df['DEF_RIM_FG_PCT'] * 100

    merge_df = pd.merge(passing_df, possession_df, on='PLAYER_NAME', how='outer')
    merge_df = pd.merge(merge_df, rebounding_df, on='PLAYER_NAME', how='outer')
    merge_df = pd.merge(merge_df, defense_df, on='PLAYER_NAME', how='outer')

    return merge_df


def get_hustle_stats_for_data(game_date, year):
    hustle_ep = HustleStats()
    hustle_df = hustle_ep.get_data({
        'DateFrom': game_date,
        'DateTo': game_date,
        'Season': year
    })[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'MIN', 'CONTESTED_SHOTS_2PT', 'CONTESTED_SHOTS_3PT', 'CHARGES_DRAWN',
        'DEFLECTIONS', 'LOOSE_BALLS_RECOVERED', 'SCREEN_ASSISTS']]
    return hustle_df


def get_stats_for_game(game_id, year, game_date, file_path, data_override=False):
    pbp_df = merge_shot_pbp_for_game(year, game_id, override_file=data_override)
    stats_df = get_scoring_stats_from_pbp(pbp_df)
    stats_df = stats_df.merge(get_tracking_stats_for_date(game_date, year), left_on='player', right_on='PLAYER_NAME',
                              how='left')
    stats_df = stats_df.merge(get_hustle_stats_for_data(game_date, year), left_on='player', right_on='PLAYER_NAME',
                              how='left')
    stats_df = stats_df.fillna(0)
    stats_df = stats_df[stats_df['TEAM_ABBREVIATION'] != 0]
    stats_df.to_json(file_path, orient='records')


def get_data_for_game(game_id, game_date, year='2017-18'):
    get_rotation_data_for_game(game_id, year=year, single_game_file_path=file_dir)
    # get_shot_data_for_game(game_id, season=year, file_path=file_dir + 'shots.json', data_override=False)
    # get_stats_for_game(game_id, year, game_date, file_dir + 'stats.json', data_override=True)


get_data_for_game('0021700807', '02/07/2018')
