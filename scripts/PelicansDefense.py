from util.data import PlayByPlay, TeamAdvancedGameLogs, convert_time
import pandas as pd

pbp_ep = PlayByPlay()
log_ep = TeamAdvancedGameLogs()


def is_home(team_df):
    home_df = team_df[team_df['VISITORDESCRIPTION'].isnull()]
    vis_df = team_df[team_df['HOMEDESCRIPTION'].isnull()]
    return len(home_df) > len(vis_df)


def get_data_for_game(game_id, season, team):
    pbp_df = pbp_ep.get_data({'GameID': game_id, 'Season': season})

    shots_df = pbp_df[pbp_df['EVENTMSGTYPE'].isin([1, 2])]
    shots_df['TIME'] = convert_time(shots_df['PCTIMESTRING'], shots_df['PERIOD'])

    team_shots_df = shots_df[shots_df['PLAYER1_TEAM_ABBREVIATION'] == team]

    players = team_shots_df['PLAYER1_NAME'].unique()

    team_is_home = is_home(team_shots_df)

    data = {}
    for player in players:
        data[player] = {'Player': player,
                        'Game': game_id,
                        '2PT Make': 0,
                        '3PT Make': 0,
                        '2PT Miss': 0,
                        '3PT Miss': 0,
                        'Opp Pts After 2PT Make': 0,
                        'Opp Pts After 3PT Make': 0,
                        'Opp Pts After 2PT Miss': 0,
                        'Opp Pts After 3PT Miss': 0,
                        'Shot Not Followed': 0,
                        'Time Diff After 2PT Make': 0,
                        'Time Diff After 3PT Make': 0,
                        'Time Diff After 2PT Miss': 0,
                        'Time Diff After 3PT Miss': 0
                        }

    team_desc = 'HOMEDESCRIPTION' if team_is_home else 'VISITORDESCRIPTION'
    opp_desc = 'VISITORDESCRIPTION' if team_is_home else 'HOMEDESCRIPTION'

    for ix, shot in team_shots_df.iterrows():
        team_shooter = shot['PLAYER1_NAME']
        shot_value = '3PT' if '3PT' in shot[team_desc] else '2PT'

        if len(shots_df[shots_df['TIME'] > shot['TIME']]) > 0:
            next_shot = shots_df[shots_df['TIME'] > shot['TIME']].iloc[0]

            if shot['PERIOD'] != next_shot['PERIOD']:
                data[team_shooter]['Shot Not Followed'] += 1
                continue

            time_diff = (next_shot['TIME'] - shot['TIME'])
            if time_diff > 30:
                data[team_shooter]['Shot Not Followed'] += 1
                continue

            if next_shot['PLAYER1_TEAM_ABBREVIATION'] != team:
                shot_category = 'Make' if shot['EVENTMSGTYPE'] == 1 else 'Miss'
                data[team_shooter][shot_value + ' ' + shot_category] += 1
                data[team_shooter]['Time Diff After ' + shot_value + ' ' + shot_category] += time_diff

                if next_shot['EVENTMSGTYPE'] == 1:
                    next_shot_value = 3 if '3PT' in next_shot[opp_desc] else 2
                    data[team_shooter]['Opp Pts After ' + shot_value + ' ' + shot_category] += next_shot_value

            else:
                data[team_shooter]['Shot Not Followed'] += 1
        else:
            data[team_shooter]['Shot Not Followed'] += 1

    df_data = []
    for dat in data:
        df_data.append(data[dat])

    data_df = pd.DataFrame(df_data)
    #
    # data_df['Efg 2PT Make'] = data_df['Opp Pts After 2PT Make'] / data_df['2PT Make']
    # data_df['Efg 3PT Make'] = data_df['Opp Pts After 3PT Make'] / data_df['2PT Make']
    # data_df['Efg 2PT Miss'] = data_df['Opp Pts After 2PT Miss'] / data_df['2PT Miss']
    # data_df['Efg 3PT Miss'] = data_df['Opp Pts After 3PT Miss'] / data_df['2PT Miss']

    return data_df


def get_data_for_season(season, team):
    log_df = log_ep.get_data({'Season': season})
    log_df = log_df[log_df['TEAM_ABBREVIATION'] == team]

    games = log_df['GAME_ID'].unique()
    season_df = pd.DataFrame()
    for game in games:
        game = str(game)
        if len(game) < 10:
            game = '00' + str(game)
        game_df = get_data_for_game(game, season, team)
        season_df = season_df.append(game_df)

    players = season_df['Player'].unique()
    data = []
    for player in players:
        player_df = season_df[season_df['Player'] == player]
        player_data = {'Player': player}
        for col in player_df.columns:
            if col not in ['Player', 'Game']:
                player_data[col] = player_df[col].sum()
        data.append(player_data)

    sum_df = pd.DataFrame(data)
    sum_df['Efg 2PT Make'] = round((sum_df['Opp Pts After 2PT Make'] / sum_df['2PT Make']) * 100, 2)
    sum_df['Efg 3PT Make'] = round((sum_df['Opp Pts After 3PT Make'] / sum_df['3PT Make']) * 100, 2)
    sum_df['Efg 2PT Miss'] = round((sum_df['Opp Pts After 2PT Miss'] / sum_df['2PT Miss']) * 100, 2)
    sum_df['Efg 3PT Miss'] = round((sum_df['Opp Pts After 3PT Miss'] / sum_df['3PT Miss']) * 100, 2)
    sum_df['Avg Time Diff After 2PT Make'] = round(sum_df['Time Diff After 2PT Make'] / sum_df['2PT Make'], 2)
    sum_df['Avg Time Diff After 3PT Make'] = round(sum_df['Time Diff After 3PT Make'] / sum_df['3PT Make'], 2)
    sum_df['Avg Time Diff After 2PT Miss'] = round(sum_df['Time Diff After 2PT Miss'] / sum_df['2PT Miss'], 2)
    sum_df['Avg Time Diff After 3PT Miss'] = round(sum_df['Time Diff After 3PT Miss'] / sum_df['3PT Miss'], 2)

    for col in sum_df.columns:
        if col != 'Player':
            sum_df[col] = round(sum_df[col], 2)

    return sum_df


df = get_data_for_season('2017-18', 'NOP')
team_data = {'Player': 'Team'}
for col in ['2PT Make', '3PT Make', '2PT Miss', '3PT Miss']:
    team_data['Efg ' + col] = round(df['Opp Pts After ' + col].sum() / df[col].sum(), 2)
    team_data['Avg Time Diff After ' + col] = round(df['Time Diff After ' + col].sum() / df[col].sum(), 2)
df = df.append(pd.DataFrame([team_data]))
df = df.fillna(0)

df.to_csv('Pels.csv')
None
