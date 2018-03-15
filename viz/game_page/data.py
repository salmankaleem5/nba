from viz.rotations.data import get_rotation_data_for_game, is_home
from viz.shotCharts.data import get_shot_data_for_game
from util.util import merge_shot_pbp_for_game
from util.nba_stats import TrackingStats, HustleStats, GeneralPlayerStats, Matchups
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


def get_stats_from_pbp(pbp_df):
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
        ast = len(assist_df)
        ast_pts = ((len(assist_df[assist_df['SHOT_TYPE'] == '3PT Field Goal'])) * 3) + (
                (len(assist_df[assist_df['SHOT_TYPE'] == '2PT Field Goal'])) * 2)

        rebound_df = player_df[player_df['EVENTMSGTYPE'] == 4]
        if len(rebound_df) > 0:
            rebound_str = rebound_df.iloc[-1][desc]
            off_reb = int(str(rebound_str.split('Off:')[1]).split(' ')[0])
            def_reb = int(str(rebound_str.split('Def:')[1]).split(')')[0])
        else:
            off_reb = 0
            def_reb = 0

        p_data = {
            'player': p,
            'and_one': ft1a,
            '2pt_ft': ft2a,
            '3pt_ft': ft3a,
            'tech_ft': ft_tech,
            'ftm': ftm,
            '2pt_fga': fg2a,
            '2pt_fgm': fg2m,
            '3pt_fga': fg3a,
            '3pt_fgm': fg3m,
            'pts': pts,
            'tsa': tsa,
            'eff': round(eff * 100, 2),
            'ast': ast,
            'ast_pts': ast_pts,
            'oreb': off_reb,
            'dreb': def_reb
        }
        player_data.append(p_data)

    return pd.DataFrame(player_data)


def get_tracking_stats_for_date(game_date, year, data_override=False):
    tracking_ep = TrackingStats()

    try:
        all_cols = []
        passing_cols = ['POTENTIAL_AST', 'PASSES_MADE']
        poss_cols = ['FRONT_CT_TOUCHES', 'TIME_OF_POSS', 'ELBOW_TOUCHES', 'POST_TOUCHES', 'PAINT_TOUCHES']
        reb_cols = ['OREB_CHANCES', 'OREB_CHANCE_DEFER', 'OREB_CHANCE_PCT_ADJ', 'DREB_CHANCES',
                    'DREB_CHANCE_DEFER', 'DREB_CHANCE_PCT_ADJ', 'REB', 'REB_CHANCES', 'REB_CHANCE_DEFER',
                    'REB_CHANCE_PCT_ADJ']
        def_cols = ['BLK', 'STL', 'DEF_RIM_FGM', 'DEF_RIM_FGA', 'DEF_RIM_FG_PCT']

        all_cols.extend(passing_cols)
        all_cols.extend(poss_cols)
        all_cols.extend(reb_cols)
        all_cols.extend(def_cols)

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

        rebounding_df = tracking_ep.get_data({
            'PtMeasureType': 'Rebounding',
            'DateFrom': game_date,
            'DateTo': game_date,
            'Season': year
        }, override_file=data_override)[['PLAYER_NAME'] + reb_cols]

        rebounding_df['OREB_CHANCE_PCT_ADJ'] = rebounding_df['OREB_CHANCE_PCT_ADJ'] * 100
        rebounding_df['DREB_CHANCE_PCT_ADJ'] = rebounding_df['DREB_CHANCE_PCT_ADJ'] * 100

        defense_df = tracking_ep.get_data({
            'PtMeasureType': 'Defense',
            'DateFrom': game_date,
            'DateTo': game_date,
            'Season': year
        }, override_file=data_override)[['PLAYER_NAME'] + def_cols]

        defense_df['DEF_RIM_FG_PCT'] = defense_df['DEF_RIM_FG_PCT'] * 100

        merge_df = pd.merge(passing_df, possession_df, on='PLAYER_NAME', how='outer')
        merge_df = pd.merge(merge_df, rebounding_df, on='PLAYER_NAME', how='outer')
        merge_df = pd.merge(merge_df, defense_df, on='PLAYER_NAME', how='outer')

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
    pbp_df = merge_shot_pbp_for_game(year, game_id, override_file=data_override)
    stats_df = get_stats_from_pbp(pbp_df)
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


def get_matchup_data_for_game(game_id, file_path, data_override=False):
    matchup_df = Matchups().get_data({'GameID': game_id}, override_file=data_override)

    matchup_df.to_json(file_path, orient='records')


def get_data_for_game(game_id, game_date, year='2017-18', data_override=False):
    get_rotation_data_for_game(game_id, year=year, file_path=file_dir)
    get_shot_data_for_game(game_id, season=year, file_path=file_dir + 'shots.json', data_override=data_override)
    get_stats_for_game(game_id, year, game_date, file_dir + 'stats.json', data_override=data_override)
    get_matchup_data_for_game(game_id, file_dir + 'matchups.json', data_override=data_override)


get_data_for_game('0021701017', '03/14/2018', data_override=True)
