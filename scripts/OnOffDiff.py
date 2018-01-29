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

onOffDf = onOffDf[onOffDf.MIN_ON >= 500].sort_values(by='OFF_DIFF', ascending=False)

print_reddit_table(onOffDf,
                   ['VS_PLAYER_NAME', 'TEAM_ABBREVIATION', 'OFF_DIFF', 'DEF_DIFF', 'NET_DIFF'])
