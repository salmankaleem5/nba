from util.nba_stats import PlayByPlay, TeamAdvancedGameLogs
from util.data import file_check
import sys
import pandas as pd

from util.format import convert_time

season = '2017-18'
season_file_path = './multi_game/data.csv'


# From the pbp_df and a team abbreviation, determines if the team is home or visitor
# Returns true if team is home
def is_home(df, t):
    df = df[df['PLAYER1_TEAM_ABBREVIATION'] == t]
    home_df = df[df['VISITORDESCRIPTION'].isnull()]
    vis_df = df[df['HOMEDESCRIPTION'].isnull()]
    return len(home_df) > len(vis_df)


# From pbp_df and a team abbreviation, returns a df of all subs for that team
def get_team_df(df, t):
    team_is_home = is_home(df, t)
    df = df[df['PLAYER1_TEAM_ABBREVIATION'].notnull()]
    if team_is_home:
        return df[df['VISITORDESCRIPTION'].isnull()]
    else:
        return df[df['HOMEDESCRIPTION'].isnull()]


# Get initial lineups for a Period.
# First look for players who are subbed out before they are subbed in
# If less than 5 players meet initial criteria looks for players who were listed in pbp but never subbed in or out
# If still less than 5 players, throw value error and throw out the period
def get_initial_lineup(df):
    subs_df = df[df.EVENTMSGTYPE == 8]
    initial_players = []
    subbed_in = []
    end = 0
    for ix, sub in subs_df.iterrows():
        if end == 0:
            end = sub.TIME

        player_in = sub.PLAYER2_NAME
        player_out = sub.PLAYER1_NAME

        if player_out not in subbed_in:
            initial_players.append(player_out)

        subbed_in.append(player_in)

        if len(initial_players) == 5:
            return {
                'players': initial_players,
                'start_time': (df.iloc[0]['PERIOD'] - 1) * 720,
                'end_time': end
            }

    others = df.PLAYER1_NAME.unique()
    others = [str(i) for i in others]
    others = list(filter(lambda x: x != 'nan', others))
    others = list(filter(lambda x: x not in subbed_in, others))
    others = list(filter(lambda x: x not in initial_players, others))

    for p in others:
        if p not in initial_players:
            initial_players.append(p)
            if len(initial_players) == 5:
                return {
                    'players': initial_players,
                    'start_time': (df.iloc[0]['PERIOD'] - 1) * 720,
                    'end_time': end
                }

    raise ValueError('Not enough players')


def get_game_lineups_for_team(team_df):
    lineups = []

    period_max = team_df['PERIOD'].max()
    if period_max < 4:
        raise ValueError('PERIOD MAX IS LOWER THAN 4')

    for p in range(1, (period_max + 1)):
        period_df = team_df[team_df['PERIOD'] == p]

        try:
            initial_lineup = get_initial_lineup(period_df)
        except ValueError:
            print(ValueError)
            continue
        lineups.append(initial_lineup)

        current_players = initial_lineup['players']

        subs_df = period_df[period_df.EVENTMSGTYPE == 8][['PLAYER1_NAME', 'PLAYER2_NAME', 'TIME']]
        for jx, s in subs_df.iterrows():
            p_out = s.PLAYER1_NAME
            p_in = s.PLAYER2_NAME

            if p_out not in current_players:
                raise ValueError('SUB OUT IS NOT IN CURRENT PLAYERS')

            current_players = list(filter(lambda x: x != p_out, current_players))
            current_players.append(p_in)

            lineups.append({
                'players': current_players,
                'start_time': s.TIME
            })

    for i in range(0, len(lineups)):
        if i < len(lineups) - 1:
            lineups[i]['end_time'] = lineups[i + 1]['start_time']
        else:
            lineups[i]['end_time'] = 2880 if period_max == 4 else 2880 + ((period_max - 4) * 300)

    lineups = list(filter(lambda x: x['start_time'] != x['end_time'], lineups))

    return lineups


def get_game_player_stints_for_team(team_lineups):
    players = []
    for line_up in team_lineups:
        for player in line_up['players']:
            if player not in players:
                players.append(player)

    team_player_stints = []
    for player in players:
        player_lineups = list(filter(lambda x: player in x['players'], team_lineups))

        player_stints = []
        previous_start_time = player_lineups[0]['start_time']
        previous_end_time = player_lineups[0]['end_time']

        for line_up in player_lineups[1:]:
            if line_up['start_time'] == previous_end_time:
                previous_end_time = line_up['end_time']
            else:
                player_stints.append({
                    'player': player,
                    'start_time': previous_start_time,
                    'end_time': previous_end_time
                })
                previous_start_time = line_up['start_time']
                previous_end_time = line_up['end_time']

        player_stints.append({
            'player': player,
            'start_time': previous_start_time,
            'end_time': previous_end_time
        })

        team_player_stints.extend(player_stints)

    team_player_stints_df = pd.DataFrame(team_player_stints)
    team_player_stints_df['time'] = team_player_stints_df['end_time'] - team_player_stints_df['start_time']

    return team_player_stints_df


def transform_stints_for_viz(player_stints_df, include_ot=True):
    data = []
    minute_max = int(player_stints_df['end_time'].max() / 60) if include_ot else 48
    for player in player_stints_df['player'].unique():
        player_df = player_stints_df[player_stints_df['player'] == player]
        for minute in range(0, minute_max):
            minute_start = minute * 60
            minute_end = (minute + 1) * 60

            if minute == minute_max - 1:
                minute_end += 1

            time_missed_before = player_df['start_time'].map(
                lambda x: 0 if x <= minute_start else 60 if x >= minute_end else x - minute_start)
            time_missed_after = player_df['end_time'].map(
                lambda x: 0 if x >= minute_end else 60 if x <= minute_start else minute_end - x)

            time_in_minute = (60 - time_missed_before - time_missed_after).sum()

            data.append({
                'player': player,
                'minute': str(minute + 1),
                'value': time_in_minute
            })

    return pd.DataFrame(data)


def get_score_data_for_game(game):
    pbp_ep = PlayByPlay()

    pbp_df = pbp_ep.get_data({'Season': season, 'GameID': game}, override_file=False)
    pbp_df['TIME'] = convert_time(pbp_df['PCTIMESTRING'], pbp_df['PERIOD']) / 60

    pbp_df = pbp_df[pbp_df['SCOREMARGIN'].notnull()]
    pbp_df = pbp_df[pbp_df['PLAYER1_ID'].notnull()]

    pbp_df['SCOREMARGIN'] = pbp_df['SCOREMARGIN'].map(lambda x: 0 if x == 'TIE' else x)

    pbp_df = pbp_df.rename(columns={'SCOREMARGIN': 'score_margin', 'TIME': 'minute'})
    pbp_df = pbp_df[['score_margin', 'minute']]

    initial_row = [{'score_margin': 0, 'minute': 0}]

    pbp_df = pd.concat([pd.DataFrame(initial_row), pbp_df], ignore_index=True)

    return pbp_df


def get_viz_data_for_team_season(team_abbreviation, last_n_games=''):
    log = TeamAdvancedGameLogs().get_data({'Season': season, 'LastNGames': last_n_games}, override_file=True)
    log = log[log['TEAM_ABBREVIATION'] == team_abbreviation]

    pbp_ep = PlayByPlay()

    season_player_stints_df = pd.DataFrame()
    games = log.GAME_ID.tolist()
    for game in games:
        game = str(game)
        if len(game) < 10:
            game = '00' + str(game)

        pbp_df = pbp_ep.get_data({'Season': season, 'GameID': game})
        pbp_df['TIME'] = convert_time(pbp_df['PCTIMESTRING'], pbp_df['PERIOD'])

        team_df = get_team_df(pbp_df, team_abbreviation)
        team_lineups = get_game_lineups_for_team(team_df)
        game_stints_df = get_game_player_stints_for_team(team_lineups)
        season_player_stints_df = season_player_stints_df.append(game_stints_df)

    rotation_data = transform_stints_for_viz(season_player_stints_df, include_ot=False)

    starters = season_player_stints_df[season_player_stints_df['start_time'] == 0]['player'].unique()
    starters = sorted(starters,
                      key=lambda x: -len(season_player_stints_df[
                          (season_player_stints_df['player'] == x) & (season_player_stints_df['start_time'] == 0)
                          ])
                      )
    starters = starters[:5]
    starters = sorted(starters,
                      key=lambda x: -season_player_stints_df[
                          season_player_stints_df['player'] == x
                          ]['time'].sum())

    bench = season_player_stints_df[~season_player_stints_df['player'].isin(starters)]['player'].unique()
    bench = sorted(bench,
                   key=lambda x: -season_player_stints_df[
                       season_player_stints_df['player'] == x
                       ]['time'].sum())

    players = starters + bench

    index = 1
    rotation_data['pindex'] = 0
    for player in players:
        sys.stdout.write("\"" + player + "\",")
        cond = rotation_data.player == player
        rotation_data.pindex[cond] = index
        index += 1

    file_check(season_file_path)
    rotation_data.to_csv(season_file_path)


def get_rotation_data_for_game(game_id, year='2017-18', single_game_file_path='./single_game/'):
    pbp_ep = PlayByPlay()

    game_id = str(game_id)
    if len(game_id) < 10:
        game_id = '00' + str(game_id)

    pbp_df = pbp_ep.get_data({'Season': year, 'GameID': game_id})
    pbp_df['TIME'] = convert_time(pbp_df['PCTIMESTRING'], pbp_df['PERIOD'])

    teams = pbp_df['PLAYER1_TEAM_ABBREVIATION'].unique()[1:]
    rotation_df = pd.DataFrame()
    index = 1
    for t in teams:
        team_df = get_team_df(pbp_df, t)
        team_lineups = get_game_lineups_for_team(team_df)
        team_game_player_stints_df = get_game_player_stints_for_team(team_lineups)
        team_rotation_df = transform_stints_for_viz(team_game_player_stints_df)

        starters = team_game_player_stints_df[team_game_player_stints_df['start_time'] == 0]['player'].unique()
        starters = sorted(starters,
                          key=lambda x: -team_game_player_stints_df[
                              team_game_player_stints_df['player'] == x
                              ]['time'].sum())

        bench = team_game_player_stints_df[~team_game_player_stints_df['player'].isin(starters)]['player'].unique()
        bench = sorted(bench,
                       key=lambda x: -team_game_player_stints_df[
                           team_game_player_stints_df['player'] == x
                           ]['time'].sum())

        players = starters + bench
        team_rotation_df['pindex'] = 0
        for player in players:
            cond = team_rotation_df.player == player
            team_rotation_df.pindex[cond] = index
            index += 1

        index += 1

        rotation_df = rotation_df.append(team_rotation_df)

    file_check(single_game_file_path)
    rotation_df.to_json(single_game_file_path + 'rotations.json', orient='records')

    score_df = get_score_data_for_game(game_id)
    score_df.to_json(single_game_file_path + 'score.json', orient='records')


#get_viz_data_for_team_season('NOP', last_n_games='9')
