from util.data_scrappers.nba_stats import GeneralTeamStats
from util.format import print_reddit_table
from math import pow
import pandas as pd

team_stats = GeneralTeamStats()

advanced_df = team_stats.get_data({'Season': '2017-18', 'MeasureType': 'Advanced'}, override_file=True)

data = []
for ix, t in advanced_df.iterrows():
    exp_pct = pow(t.OFF_RATING, 13.91) / (pow(t.OFF_RATING, 13.91) + pow(t.DEF_RATING, 13.91))
    data.append(
        {
            'Team': t.TEAM_NAME,
            'Actual Win%': t.W_PCT * 100,
            'Net Rating': t.OFF_RATING - t.DEF_RATING,
            'Actual Wins': t.W,
            'Expected Win%': exp_pct * 100,
            'Expected Wins': exp_pct * t.GP
        }
    )

df = pd.DataFrame(data)
df['% Diff'] = df['Actual Win%'] - df['Expected Win%']
df['Wins Above Exp'] = df['Actual Wins'] - df['Expected Wins']
print_reddit_table(df.sort_values(by='% Diff', ascending=False),
                   ['Team', 'Net Rating', 'Actual Win%', 'Expected Win%', '% Diff', 'Wins Above Exp'])
