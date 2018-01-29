from util.nba_stats import PlayByPlay, TeamAdvancedGameLogs
from util.data import file_check
import sys
import pandas as pd

from util.format import convert_time

season = '2017-18'
season_file_path = './multi_game/data.csv'
single_game_file_path = './single_game/'


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
    if team_is_home:
        return df[df['VISITORDESCRIPTION'].isnull()]
    else:
        return df[df['HOMEDESCRIPTION'].isnull()]


def get_initial_lineup(df):
    subs_df = df[df.EVENTMSGTYPE == 8]
    players = []
    subbed_in = []
    end = 0
    for ix, sub in subs_df.iterrows():
        if end == 0:
            end = sub.TIME
        player_in = sub.PLAYER2_NAME
        player_out = sub.PLAYER1_NAME
        if player_out not in subbed_in:
            players.append(player_out)
        subbed_in.append(player_in)
        if len(players) == 5:
            return {
                'players': players,
                'start_time': (df.iloc[0]['PERIOD'] - 1) * 720,
                'end_time': end
            }

    others = df.PLAYER1_NAME.unique()
    others = [str(i) for i in others]
    others = list(filter(lambda x: x != 'nan', others))
    others = list(filter(lambda x: x != 'None', others))
    others = list(filter(lambda x: x not in subbed_in, others))
    for p in others:
        if p not in players:
            players.append(p)
            if len(players) == 5:
                return {
                    'players': players,
                    'start_time': (df.iloc[0]['PERIOD'] - 1) * 720,
                    'end_time': end
                }

    raise ValueError('Not enough players')


def get_lineups_for_team(team_df):
    lineups = []
    for p in range(1, 5):
        period_df = team_df[team_df['PERIOD'] == p]
        initial_lineup = get_initial_lineup(period_df)
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
            lineups[i]['end_time'] = 2880

    lineups = list(filter(lambda x: x['start_time'] != x['end_time'], lineups))

    return lineups


def get_game_player_stints_for_team(df, t):
    team_df = get_team_df(df, t)
    team_lineups = get_lineups_for_team(team_df)
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


def transform_stints_for_viz(df):
    data = []
    for player in df['player'].unique():
        player_df = df[df['player'] == player]
        for minute in range(0, 48):
            minute_start = minute * 60
            minute_end = (minute + 1) * 60

            if minute == 47:
                minute_end += 1

            df1 = player_df[player_df['start_time'] >= minute_start]
            df1 = df1[df1['start_time'] < minute_end - 30]

            df2 = player_df[player_df['end_time'] > minute_start + 30]
            df2 = df2[df2['end_time'] <= minute_end]

            df3 = player_df[player_df['start_time'] < minute_start]
            df3 = df3[df3['end_time'] > minute_end]

            merge_df = pd.merge(df1, df2, on=['player', 'start_time', 'end_time'], how='outer')
            merge_df = pd.merge(merge_df, df3, on=['player', 'start_time', 'end_time'], how='outer')

            data.append({
                'player': player,
                'minute': str(minute + 1),
                'value': len(merge_df)
            })

    return pd.DataFrame(data)


def get_score_data_for_game(game):
    pbp_ep = PlayByPlay()

    data = []
    for m in range(1, 49):
        data.append({'minute': m, 'score_margin': 0})

    pbp_df = pbp_ep.get_data({'Season': season, 'GameID': game}, override_file=False)
    pbp_df['TIME'] = convert_time(pbp_df['PCTIMESTRING'], pbp_df['PERIOD'])

    pbp_df = pbp_df[pbp_df['SCOREMARGIN'].notnull()]
    pbp_df = pbp_df[pbp_df['PLAYER1_ID'].notnull()]

    previous_score_margin = 0
    for m in range(0, 48):
        minute_start = m * 60
        minute_end = (m + 1) * 60
        minute_df = pbp_df[pbp_df['TIME'] > minute_start]
        minute_df = minute_df[minute_df['TIME'] <= minute_end]

        if len(minute_df) > 0:
            score_margin = minute_df.iloc[-1]['SCOREMARGIN']
            if score_margin == 'TIE':
                score_margin = 0
            else:
                score_margin = int(score_margin)

            data[m]['score_margin'] = score_margin - previous_score_margin
            previous_score_margin = score_margin
        else:
            data[m]['score_margin'] = 0

    return pd.DataFrame(data)


def get_viz_data_for_team_season(team_abbreviation):
    log = TeamAdvancedGameLogs().get_data({'Season': season, 'LastNGames': '3'}, override_file=True)
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

        game_stints_df = get_game_player_stints_for_team(pbp_df, team_abbreviation)
        season_player_stints_df = season_player_stints_df.append(game_stints_df)

    rotation_data = transform_stints_for_viz(season_player_stints_df)

    players = season_player_stints_df['player'].unique()
    players = sorted(players,
                     key=lambda x: -season_player_stints_df[season_player_stints_df['player'] == x]['time'].sum())

    index = 1
    rotation_data['pindex'] = 0
    for player in players:
        sys.stdout.write("\"" + player + "\",")
        cond = rotation_data.player == player
        rotation_data.pindex[cond] = index
        index += 1

    file_check(season_file_path)
    rotation_data.to_csv(season_file_path)


def get_viz_data_for_game(game_id):
    pbp_ep = PlayByPlay()

    game_id = str(game_id)
    if len(game_id) < 10:
        game_id = '00' + str(game_id)

    pbp_df = pbp_ep.get_data({'Season': season, 'GameID': game_id})
    pbp_df['TIME'] = convert_time(pbp_df['PCTIMESTRING'], pbp_df['PERIOD'])

    teams = pbp_df['PLAYER1_TEAM_ABBREVIATION'].unique()[1:]
    file_index = 1
    for t in teams:
        index = 1
        game_stints_df = get_game_player_stints_for_team(pbp_df, t)
        team_rotation_data = transform_stints_for_viz(game_stints_df)

        players = game_stints_df['player'].unique()
        players = sorted(players,
                         key=lambda x: -game_stints_df[game_stints_df['player'] == x]['time'].sum())

        team_rotation_data['pindex'] = 0
        for player in players:
            sys.stdout.write("\"" + player + "\",")
            cond = team_rotation_data.player == player
            team_rotation_data.pindex[cond] = index
            index += 1

        file_check(season_file_path)
        team_rotation_data.to_csv(single_game_file_path + 'team' + str(file_index) + '.csv')
        file_index += 1

    score_df = get_score_data_for_game(game_id)
    score_df.to_csv(single_game_file_path + 'score.csv')


get_viz_data_for_team_season('NOP')
#get_viz_data_for_game('0021700692')
