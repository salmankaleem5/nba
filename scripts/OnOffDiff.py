from util.nba_stats import OnOffSummary, GeneralTeamStats
from util.reddit import print_reddit_table
import pandas as pd

onOffStats = OnOffSummary()
teamStats = GeneralTeamStats()

teams = teamStats.get_data({'Season': '2017-18'}).TEAM_ID.unique()

onOffDf = pd.DataFrame()
for t in teams:
    onOffDf = onOffDf.append(onOffStats.get_data({'TeamID': t}, override_file=False))

onOffDf['OFF_DIFF'] = onOffDf['OFF_RATING_ON'] - onOffDf['OFF_RATING_OFF']
onOffDf['DEF_DIFF'] = onOffDf['DEF_RATING_OFF'] - onOffDf['DEF_RATING_ON']
onOffDf['NET_DIFF'] = onOffDf['OFF_DIFF'] + onOffDf['DEF_DIFF']


onOffDf = onOffDf[onOffDf.MIN_ON >= 500].sort_values(by='NET_DIFF', ascending=False)

df = pd.DataFrame(columns=onOffDf.columns)
for t in onOffDf.TEAM_ABBREVIATION.unique():
    df = df.append(onOffDf[onOffDf['TEAM_ABBREVIATION'] == t].iloc[0])

print_reddit_table(df,
                   ['VS_PLAYER_NAME', 'TEAM_ABBREVIATION', 'NET_DIFF'])


onOffDf = onOffDf[onOffDf.MIN_ON >= 500].sort_values(by='NET_DIFF', ascending=True)

df = pd.DataFrame(columns=onOffDf.columns)
for t in onOffDf.TEAM_ABBREVIATION.unique():
    df = df.append(onOffDf[onOffDf['TEAM_ABBREVIATION'] == t].iloc[0])

print_reddit_table(df,
                   ['VS_PLAYER_NAME', 'TEAM_ABBREVIATION', 'NET_DIFF'])