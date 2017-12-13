from util.data import GeneralTeamStats
from util.reddit import print_reddit_table
from math import pow
import pandas as pd

team_stats = GeneralTeamStats()

advanced_df = team_stats.get_data({'Season': '2016-17', 'MeasureType': 'Advanced'})

data = []
for ix, t in advanced_df.iterrows():
    exp_pct = pow(t.OFF_RATING, 13.91) / (pow(t.OFF_RATING, 13.91) + pow(t.DEF_RATING, 13.91))
    data.append(
        {
            'Team': t.TEAM_NAME,
            'Actual_Pct': t.W_PCT * 100,
            'Actual_W': t.W,
            'Expected_Pct': exp_pct * 100,
            'Expected_W': exp_pct * t.GP
        }
    )

df = pd.DataFrame(data)
df['Diff_Pct'] = df['Actual_Pct'] - df['Expected_Pct']
df['Diff_W'] = df['Actual_W'] - df['Expected_W']
print_reddit_table(df.sort_values(by='Diff_W', ascending=False),
                   ['Team', 'Actual_Pct', 'Expected_Pct', 'Diff_Pct', 'Diff_W'])
