from util.data import data_dir, GeneralPlayerStats
import pandas as pd
import os


def get_data():
    file_path = data_dir + 'ts_pct_accuracy/' + 'full_year.csv'
    if not os.path.isfile(file_path):
        pbp_directory_name = data_dir + 'playbyplayv2/2016-17/'
        directory = os.fsencode(pbp_directory_name)

        player_free_throws = {}
        df_data = []
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            print(filename)
            game_df = pd.read_csv(pbp_directory_name + filename)
            game_df = game_df[game_df.HOMEDESCRIPTION.str.contains('Free Throw', na=False)].append(
                game_df[game_df.VISITORDESCRIPTION.str.contains('Free Throw', na=False)])

            players = game_df.PLAYER1_NAME.unique()

            for player in players:
                player_df = game_df[game_df.PLAYER1_NAME == player]

                ft1 = len(player_df[player_df.HOMEDESCRIPTION.str.contains('of 1', na=False)]) + len(
                    player_df[player_df.VISITORDESCRIPTION.str.contains('of 1', na=False)])

                ft2 = (len(player_df[player_df.HOMEDESCRIPTION.str.contains('of 2', na=False)]) + len(
                    player_df[player_df.VISITORDESCRIPTION.str.contains('of 2', na=False)])) / 2

                ft3 = (len(player_df[player_df.HOMEDESCRIPTION.str.contains('of 3', na=False)]) + len(
                    player_df[player_df.VISITORDESCRIPTION.str.contains('of 3', na=False)])) / 3

                if player in player_free_throws:
                    player_free_throws[player]['ft1'] += ft1
                    player_free_throws[player]['ft2'] += ft2
                    player_free_throws[player]['ft3'] += ft3
                else:
                    player_free_throws[player] = {}
                    player_free_throws[player]['player'] = player
                    player_free_throws[player]['ft1'] = ft1
                    player_free_throws[player]['ft2'] = ft2
                    player_free_throws[player]['ft3'] = ft3

        for player in player_free_throws:
            df_data.append(player_free_throws[player])

        ft_df = pd.DataFrame(df_data)

        base_df = GeneralPlayerStats().get_data(
            {'MeasureType': 'Base', 'Season': '2016-17', 'SeasonType': 'Regular Season', 'PerMode': 'Totals'})

        merge_df = pd.merge(ft_df, base_df, right_on='PLAYER_NAME', left_on='player')
        merge_df = merge_df[['PLAYER_NAME', 'PTS', 'FGA', 'FTA', 'ft1', 'ft2', 'ft3']]
        merge_df['TS'] = merge_df['PTS'] / (2 * (merge_df['FGA'] + (0.44 * merge_df['FTA'])))
        merge_df['TS+'] = merge_df['PTS'] / (2 * (merge_df['FGA'] + merge_df['ft2'] + merge_df['ft3']))
        merge_df['DIFF'] = merge_df['TS'] - merge_df['TS+']
        merge_df = merge_df.sort_values(by='PTS')
        merge_df.to_csv(file_path)
        return merge_df
    else:
        return pd.read_csv(file_path)


df = get_data()
total_fta = df.ft1.sum() + (2 * df.ft2.sum()) + (3 * df.ft3.sum())
total_poss = df.ft2.sum() + df.ft3.sum()
poss_to_fta = total_poss / total_fta
print(poss_to_fta)
