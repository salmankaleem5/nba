from util.rotations import get_team_df, get_game_lineups_for_team, get_game_player_stints_for_team
from util.format import convert_time
from util.data_scrappers.nba_stats import TeamAdvancedGameLogs, PlayByPlay, GeneralPlayerStats
from util.data import data_dir
import pandas as pd


def get_player_stints_for_season(season):
    game_log = TeamAdvancedGameLogs().get_data({'Season': season})['GAME_ID'].unique()

    pbp_ep = PlayByPlay()

    stints_df = pd.DataFrame()

    ix = 0
    for game in game_log:
        print(str(ix) + '/' + str(len(game_log)))
        ix += 1

        game_id = str(game)
        if len(game_id) < 10:
            game_id = '00' + str(game_id)

        pbp_df = pbp_ep.get_data({'Season': season, 'GameID': game_id})
        pbp_df['TIME'] = convert_time(pbp_df['PCTIMESTRING'], pbp_df['PERIOD'])

        teams = pbp_df['PLAYER1_TEAM_ABBREVIATION'].unique()[1:]

        for team in teams:
            team_df = get_team_df(pbp_df, team)
            try:
                team_lineups = get_game_lineups_for_team(team_df)
            except ValueError:
                print(ValueError)
                continue
            team_game_player_stints_df = get_game_player_stints_for_team(team_lineups)
            stints_df = stints_df.append(team_game_player_stints_df)

    return stints_df


def analyze_stint_data(stints_df, season):
    player_stats = GeneralPlayerStats().get_data({'Season': season, 'MeasureType': 'Base', 'PerMode': 'PerGame'},
                                                 override_file=True)[['PLAYER_NAME', 'MIN', 'GP']]

    player_stats = player_stats[(player_stats['MIN'] >= 20) & (player_stats['GP'] >= 20)]

    data = []
    for ix, player in player_stats.iterrows():
        player_stints = stints_df[stints_df['player'] == player.PLAYER_NAME]
        average_stint_time = player_stints['time'].mean()
        data.append({
            'player': player.PLAYER_NAME,
            'average_stint': average_stint_time,
            'seconds_per_game': player.MIN * 60,
            'game': player.GP,
            'stints_per_game': len(player_stints) / player.GP,
            '10_min_stints': len(player_stints[player_stints['time'] >= 10 * 60]),
            '15_min_stints': len(player_stints[player_stints['time'] >= 15 * 60]),
            '20_min_stints': len(player_stints[player_stints['time'] >= 20 * 60]),
            '25_min_stints': len(player_stints[player_stints['time'] >= 25 * 60]),
            '30_min_stints': len(player_stints[player_stints['time'] >= 30 * 60]),
        })

    data_df = pd.DataFrame(data)
    data_df['mpg_to_stint'] = data_df['seconds_per_game'] / data_df['average_stint']
    data_df = data_df.sort_values(by='30_min_stints', ascending=False)
    return data_df


df = get_player_stints_for_season('2017-18')
df1 = analyze_stint_data(df, '2017-18')
df1.to_csv(data_dir + 'player_stint_data.csv')
