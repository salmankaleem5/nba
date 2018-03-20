from util.nba_stats import BoxScoreMatchups, GeneralPlayerStats
from util.data import data_dir
from scripts import Position
import pandas as pd


def compare_to_normal_offense():
    matchup_ep = BoxScoreMatchups()
    general_stats_ep = GeneralPlayerStats()

    matchup_df = matchup_ep.aggregate_data(override_file=False)
    matchup_df['EFG'] = ((matchup_df['FG3M'] * 3) + ((matchup_df['FGM'] - matchup_df['FG3M']) * 2)) / (matchup_df['FGA']) * 50

    general_stats_df = general_stats_ep.get_data(
        {'Season': '2017-18', 'PerMode': 'Per100Possessions', 'MeasureType': 'Base'}, override_file=True)

    stat_cols = ['AST', 'FG3A', 'FG3M', 'FGA', 'FGM', 'FTM']
    general_stats_df = general_stats_df[['PLAYER_NAME'] + stat_cols]

    general_stats_df['OFF_PLAYER_EFG'] = ((general_stats_df['FG3M'] * 3) + (
                (general_stats_df['FGM'] - general_stats_df['FG3M']) * 2)) / (general_stats_df['FGA']) * 50

    for sc in stat_cols:
        general_stats_df = general_stats_df.rename(columns={sc: 'OFF_PLAYER_' + sc + '_PER_100'})

    matchup_df = pd.merge(matchup_df, general_stats_df, left_on='OFF_PLAYER', right_on='PLAYER_NAME', how='left')

    for sc in stat_cols:
        matchup_df[sc + '_ABOVE_EXP'] = matchup_df[sc] - (matchup_df['OFF_PLAYER_' + sc + '_PER_100'] / 100 * matchup_df['POSS'])
    matchup_df['EFG_ABOVE_EXP'] = matchup_df['EFG'] - matchup_df['OFF_PLAYER_EFG']

    matchup_df.to_csv(data_dir + 'Matchup_per_100_comp.csv')


def compare_position():
    matchup_ep = BoxScoreMatchups()
    general_stats_ep = GeneralPlayerStats()

    matchup_df = matchup_ep.aggregate_data(override_file=False)
    position_df = Position.determine_from_listed_position()[['PLAYER_NAME', 'POSITION']]

    matchup_df = matchup_df.merge(position_df, left_on=['OFF_PLAYER'], right_on='PLAYER_NAME', how='left')
    matchup_df = matchup_df.rename(columns={'POSITION': 'OFF_PLAYER_POSITION'})

    matchup_df = matchup_df.merge(position_df, left_on=['DEF_PLAYER'], right_on='PLAYER_NAME', how='left')
    matchup_df = matchup_df.rename(columns={'POSITION': 'DEF_PLAYER_POSITION'})

    players = matchup_df['DEF_PLAYER'].unique()

    positional_matchup_data = []
    for p in players:
        player_df = matchup_df[matchup_df['DEF_PLAYER'] == p]
        if len(player_df) > 0:
            total_poss = player_df['POSS'].sum()
            positional_matchup_data.append({
                'PLAYER_NAME': p,
                'POSITION': player_df.iloc[0]['DEF_PLAYER_POSITION'],
                'GUARD_PCT': player_df[player_df['OFF_PLAYER_POSITION'] == 'Guard']['POSS'].sum() / total_poss * 100,
                'WING_PCT': player_df[player_df['OFF_PLAYER_POSITION'] == 'Wing']['POSS'].sum() / total_poss * 100,
                'BIG_PCT': player_df[player_df['OFF_PLAYER_POSITION'] == 'Big']['POSS'].sum() / total_poss * 100,
                'TOTAL_POSS': total_poss
            })

    return pd.DataFrame(positional_matchup_data).sort_values(by='TOTAL_POSS', ascending=False)


df = compare_position()
None