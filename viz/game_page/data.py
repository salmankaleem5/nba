from viz.rotations.data import get_rotation_data_for_game, get_score_data_for_game, is_home
from viz.shot_chart.util import get_shot_data_for_all_players_game
from util.util import merge_shot_pbp_for_game
from util.nba_stats import TrackingStats, HustleStats, GeneralPlayerStats, BoxScoreMatchups, BoxScoreTraditional, BoxScoreAdvanced, BoxScoreHustle, BoxScoreTracking
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


def get_game_summary(game_id, override_file=False):
    ep = BoxScoreTraditional()
    ep.set_index(1)
    df = ep.get_data({'GameID': game_id}, override_file=override_file)
    return df


def get_box_score_player_stats(game_id, override_file=False):
    traditional = BoxScoreTraditional().get_data({'GameID': game_id}, override_file=override_file)
    advanced = BoxScoreAdvanced().get_data({'GameID': game_id}, override_file=override_file)
    hustle = BoxScoreHustle().get_data({'GameID': game_id}, override_file=override_file)
    tracking = BoxScoreTracking().get_data({'GameID': game_id}, override_file=override_file)

    merge_columns = ['GAME_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_CITY', 'PLAYER_ID', 'PLAYER_NAME',
                     'START_POSITION', 'COMMENT', 'MIN']

    merge_df = pd.merge(traditional, advanced, on=merge_columns)
    merge_df = pd.merge(merge_df, tracking, on=merge_columns.extend(('FG_PCT', 'AST')))
    merge_df = pd.merge(merge_df, hustle, on=merge_columns.remove('MIN'))

    return merge_df


def get_stats_from_pbp(game_id, override_file):
    pbp_df = merge_shot_pbp_for_game('2017-18', game_id, override_file=override_file)
    players = pbp_df['PLAYER1_NAME'].unique()[1:]

    player_data = []
    for p in players:
        player_df = pbp_df[pbp_df['PLAYER1_NAME'] == p]

        desc = 'HOMEDESCRIPTION' if is_home(player_df,
                                            player_df['PLAYER1_TEAM_ABBREVIATION'].iloc[0]) else 'VISITORDESCRIPTION'

        ft_df = player_df[player_df['EVENTMSGTYPE'] == 3]
        ft1a = len(ft_df[ft_df[desc].str.contains('of 1')])
        ft2a = len(ft_df[ft_df[desc].str.contains('of 2')])
        ft3a = len(ft_df[ft_df[desc].str.contains('of 3')])
        ft_tech = len(ft_df[ft_df[desc].str.contains('Free Throw Technical')])
        ftm = len(ft_df[ft_df[desc].str.contains('PTS')])

        fg2_df = player_df[player_df['SHOT_TYPE'] == '2PT Field Goal']
        fg2a = len(fg2_df)
        fg2m = len(fg2_df[fg2_df['SHOT_MADE_FLAG'] == 1])

        fg3_df = player_df[player_df['SHOT_TYPE'] == '3PT Field Goal']
        fg3a = len(fg3_df)
        fg3m = len(fg3_df[fg3_df['SHOT_MADE_FLAG'] == 1])

        pts = (3 * fg3m) + (2 * fg2m) + ftm
        tsa = (ft2a / 2) + (ft3a / 3) + fg2a + fg3a
        eff = pts / (2 * tsa) if tsa != 0 else 0

        assist_df = pbp_df[(pbp_df['PLAYER2_NAME'] == p) & (pbp_df['SHOT_ATTEMPTED_FLAG'] == 1)]
        ast_pts = ((len(assist_df[assist_df['SHOT_TYPE'] == '3PT Field Goal'])) * 3) + (
                (len(assist_df[assist_df['SHOT_TYPE'] == '2PT Field Goal'])) * 2)

        p_data = {
            'PLAYER_NAME': p,
            'AND_ONE': ft1a,
            '2PT_FTA': ft2a,
            '3PT_FTA': ft3a,
            'TECH_FTA': ft_tech,
            '2PT_FGA': fg2a,
            '2PT_FGM': fg2m,
            '3PT_FGA': fg3a,
            '3PT_FGM': fg3m,
            'TSA': tsa,
            'EFF': round(eff * 100, 2),
            'AST_PTS': ast_pts,
        }
        player_data.append(p_data)

    return pd.DataFrame(player_data)


def get_tracking_stats_for_date(game_date, year, data_override=False):
    tracking_ep = TrackingStats()

    try:
        all_cols = []
        passing_cols = ['POTENTIAL_AST']
        poss_cols = ['TIME_OF_POSS', 'ELBOW_TOUCHES', 'POST_TOUCHES', 'PAINT_TOUCHES']
        # def_cols = ['BLK', 'STL', 'DEF_RIM_FGM', 'DEF_RIM_FGA', 'DEF_RIM_FG_PCT']

        all_cols.extend(passing_cols)
        all_cols.extend(poss_cols)
        # all_cols.extend(def_cols)

        passing_df = tracking_ep.get_data({
            'PtMeasureType': 'Passing',
            'DateFrom': game_date,
            'DateTo': game_date,
            'Season': year
        }, override_file=data_override)[['PLAYER_NAME'] + passing_cols]

        possession_df = tracking_ep.get_data({
            'PtMeasureType': 'Possessions',
            'DateFrom': game_date,
            'DateTo': game_date,
            'Season': year
        }, override_file=data_override)[['PLAYER_NAME'] + poss_cols]

        # rebounding_df = tracking_ep.get_data({
        #     'PtMeasureType': 'Rebounding',
        #     'DateFrom': game_date,
        #     'DateTo': game_date,
        #     'Season': year
        # }, override_file=data_override)[['PLAYER_NAME'] + reb_cols]
        #
        # rebounding_df['OREB_CHANCE_PCT_ADJ'] = rebounding_df['OREB_CHANCE_PCT_ADJ'] * 100
        # rebounding_df['DREB_CHANCE_PCT_ADJ'] = rebounding_df['DREB_CHANCE_PCT_ADJ'] * 100
        #
        # defense_df = tracking_ep.get_data({
        #     'PtMeasureType': 'Defense',
        #     'DateFrom': game_date,
        #     'DateTo': game_date,
        #     'Season': year
        # }, override_file=data_override)[['PLAYER_NAME'] + def_cols]
        #
        # defense_df['DEF_RIM_FG_PCT'] = defense_df['DEF_RIM_FG_PCT'] * 100

        merge_df = pd.merge(passing_df, possession_df, on='PLAYER_NAME', how='outer')
        # merge_df = pd.merge(merge_df, rebounding_df, on='PLAYER_NAME', how='outer')
        # merge_df = pd.merge(merge_df, defense_df, on='PLAYER_NAME', how='outer')

    except KeyError:
        print('Tracking Stats Not Available Yet')
        d = {'PLAYER_NAME': None}
        for c in all_cols:
            d[c] = float('nan')
        merge_df = pd.DataFrame([d])

    return merge_df


def get_hustle_stats_for_data(game_date, year, data_override=False):
    hustle_ep = HustleStats()
    hustle_df = hustle_ep.get_data({
        'DateFrom': game_date,
        'DateTo': game_date,
        'Season': year
    }, override_file=data_override)[
        ['PLAYER_NAME', 'TEAM_ABBREVIATION', 'MIN', 'CONTESTED_SHOTS_2PT', 'CONTESTED_SHOTS_3PT', 'CHARGES_DRAWN',
         'DEFLECTIONS', 'LOOSE_BALLS_RECOVERED', 'SCREEN_ASSISTS', 'BOX_OUTS']]
    return hustle_df


def get_stats_for_game(game_id, year, game_date, file_path, data_override=False):

    tracking_df = get_tracking_stats_for_date(game_date, year, data_override=data_override)
    stats_df = stats_df.merge(tracking_df, left_on='player', right_on='PLAYER_NAME', how='left')
    if len(tracking_df) == 1:
        stats_df = stats_df.fillna(-1)
    stats_df = stats_df.merge(get_hustle_stats_for_data(game_date, year, data_override=data_override), left_on='player',
                              right_on='PLAYER_NAME',
                              how='left')
    stats_df = stats_df.fillna(0)
    stats_df = stats_df[stats_df['TEAM_ABBREVIATION'] != 0]
    stats_df.to_json(file_path, orient='records')


def get_matchup_data_for_game(game_id, data_override=False):
    matchup_df = BoxScoreMatchups().get_data({'GameID': game_id}, override_file=data_override)
    return matchup_df


def get_data_for_game(game_id, game_date, year='2017-18', data_override=False):
    game_summary = get_game_summary(game_id, override_file=data_override)
    box_score = get_box_score_player_stats(game_id, override_file=data_override)
    tracking = get_tracking_stats_for_date(game_date, '2017-18', data_override=data_override)
    scoring = get_stats_from_pbp(game_id, override_file=data_override)
    rotations = get_rotation_data_for_game(game_id, year=year)
    score = get_score_data_for_game(game_id)
    shots = get_shot_data_for_all_players_game(game_id, season=year, data_override=data_override)
    matchups = get_matchup_data_for_game(game_id, data_override=data_override)

    box_score = box_score.merge(scoring, on='PLAYER_NAME')
    box_score = box_score.merge(tracking, on='PLAYER_NAME')

    game_summary.to_json('./data/game_summary.json', orient='records')
    box_score.to_json('./data/box_score.json', orient='records')
    rotations.to_json('./data/rotations.json', orient='records')
    score.to_json('./data/score.json', orient='records')
    shots.to_json('./data/shots.json', orient='records')
    matchups.to_json('./data/matchups.json', orient='records')


get_data_for_game('0021701106', '03/26/18', data_override=True)
