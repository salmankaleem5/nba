from util.nba_stats import OnOffSummary, GeneralTeamStats
from util.reddit import print_reddit_table
from util.format import get_year_string
import pandas as pd

onOffStats = OnOffSummary()
teamStats = GeneralTeamStats()


def get_on_off_for_year(season):
    teams = teamStats.get_data({'Season': season}).TEAM_ID.unique()

    on_off_df = pd.DataFrame()
    for t in teams:
        on_off_df = on_off_df.append(onOffStats.get_data({'TeamID': t, 'Season': season}, override_file=False))

    on_off_df = on_off_df[on_off_df.MIN_ON >= 1000]

    on_off_df['OFF_DIFF'] = on_off_df['OFF_RATING_ON'] - on_off_df['OFF_RATING_OFF']
    on_off_df['DEF_DIFF'] = on_off_df['DEF_RATING_OFF'] - on_off_df['DEF_RATING_ON']
    on_off_df['NET_DIFF'] = on_off_df['OFF_DIFF'] + on_off_df['DEF_DIFF']

    on_off_df['YEAR'] = season
    return on_off_df


df = pd.DataFrame()
for year in range(2007, 2018):
    year_string = get_year_string(year)
    df = df.append(get_on_off_for_year(year_string))

df = df.sort_values(by='NET_DIFF', ascending=False)
print_reddit_table(df, ['VS_PLAYER_NAME', 'YEAR', 'TEAM_ABBREVIATION', 'NET_DIFF'])
