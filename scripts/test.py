from util.nba_stats import PlayByPlay
from util.util import merged_shot_pbp

PlayByPlay().update_pbp_data('2017-18')
merged_shot_pbp('2017-18')
