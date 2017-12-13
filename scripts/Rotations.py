from util.data import PlayByPlay, TeamAdvancedGameLogs, GeneralPlayerStats, data_dir, file_check
import pandas as pd

season = '2017-18'
team = 'NOP'

# Convert PCTIMESTRING of the format MM:SS along with the quarter to absolute seconds into the game
# Returns pandas column
def convert_time(time, quarter):
    quarter.map(int)
    mins = time.map(lambda x: x.split(':')[0]).map(int)
    seconds = time.map(lambda x: x.split(':')[1]).map(int)
    return ((quarter - 1) * 12 * 60) + ((12 * 60) - (mins * 60) - seconds)


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

    others = df.PLAYER1_NAME.tolist()
    others.extend(df.PLAYER2_NAME.tolist())
    others = [str(i) for i in others]
    others = list(filter(lambda x: x != 'nan', others))
    others = list(filter(lambda x: x not in players, others))
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
            df1 = df1[df1['start_time'] < minute_end]

            df2 = player_df[player_df['end_time'] >= minute_start]
            df2 = df2[df2['end_time'] < minute_end]

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


log = TeamAdvancedGameLogs().get_data({'Season': season})
log = log[log['TEAM_ABBREVIATION'] == team]

pbp_ep = PlayByPlay()
general_ep = GeneralPlayerStats()

season_player_stints_df = pd.DataFrame()
for game in log.GAME_ID.tolist():
    game = str(game)
    if len(game) < 10:
        game = '00' + str(game)

    pbp_df = pbp_ep.get_data({'Season': season, 'GameID': game})
    pbp_df['TIME'] = convert_time(pbp_df['PCTIMESTRING'], pbp_df['PERIOD'])

    game_stints_df = get_game_player_stints_for_team(pbp_df, team)
    season_player_stints_df = season_player_stints_df.append(game_stints_df)

viz_data = transform_stints_for_viz(season_player_stints_df)

index=1
viz_data['pindex'] = 0
for player in viz_data.player.unique():
    cond = viz_data.player == player
    viz_data.pindex[cond] = index
    index += 1

file_path = data_dir + 'Rotations/viz_data.csv'
file_check(file_path)
viz_data.to_csv(file_path)