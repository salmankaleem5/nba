from util.nba_stats import PlayByPlay
from util.util import merge_shot_pbp_for_season

df = merge_shot_pbp_for_season('2017-18')

print(df['LOC_X'].max())
print(df['LOC_X'].min())
print(df['LOC_Y'].max())
print(df['LOC_Y'].min())