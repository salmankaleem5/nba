from util.data_scrappers.nba_stats import GeneralPlayerStats, TrackingStats
import pandas as pd

data_override = False

generalStats = GeneralPlayerStats()
trackingStats = TrackingStats()


def get_true_usage_for_year(year):
    base_cols = ['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'TEAM_ID', 'MIN', 'PTS', 'FGA', 'FTA', 'TOV']
    base_df = generalStats.get_data({'Season': year, 'PerMode': 'Totals', 'MeasureType': 'Base'},
                                    override_file=data_override)[base_cols]
    advanced_cols = ['PLAYER_ID', 'TEAM_ID', 'PACE', 'TS_PCT']
    advanced_df = generalStats.get_data({'Season': year, 'PerMode': 'Totals', 'MeasureType': 'Advanced'},
                                        override_file=data_override)[advanced_cols]

    passing_cols = ['PLAYER_ID', 'TEAM_ID', 'POTENTIAL_AST', 'AST_PTS_CREATED']
    passing_df = trackingStats.get_data({'Season': year, 'PerMode': 'Totals', 'PtMeasureType': 'Passing'},
                                        override_file=data_override)[passing_cols]

    merge_cols = ['PLAYER_ID', 'TEAM_ID']
    merge_df = pd.merge(base_df, advanced_df, on=merge_cols)
    merge_df = pd.merge(merge_df, passing_df, on=merge_cols)

    merge_df = merge_df[merge_df.MIN >= 100].fillna(0)
    merge_df = merge_df.sort_values(by='MIN', ascending=False).head(100)

    merge_df['POSS'] = merge_df.MIN * (merge_df.PACE / 48)

    merge_df['SCORING_USAGE'] = ((merge_df.FGA + 0.44 * merge_df.FTA) / merge_df.POSS) * 100
    merge_df['SCORING_EFF'] = merge_df.TS_PCT * 2

    merge_df['PLAYMAKING_USAGE'] = (merge_df.POTENTIAL_AST / merge_df.POSS) * 100
    merge_df['PLAYMAKING_EFF'] = merge_df.AST_PTS_CREATED / merge_df.POTENTIAL_AST

    merge_df['TOV_USAGE'] = (merge_df.TOV / merge_df.POSS) * 100

    merge_df['TOTAL_USAGE'] = merge_df.SCORING_USAGE + merge_df.PLAYMAKING_USAGE + merge_df.TOV_USAGE
    merge_df['TOTAL_EFF'] = (merge_df.PTS + merge_df.AST_PTS_CREATED) / (
        merge_df.FGA + merge_df.FTA * 0.44 + merge_df.TOV + merge_df.POTENTIAL_AST)

    merge_df['YEAR'] = year

    return merge_df[
        ['PLAYER_NAME', 'YEAR', 'SCORING_USAGE', 'PLAYMAKING_USAGE', 'TOV_USAGE', 'TOTAL_USAGE']]