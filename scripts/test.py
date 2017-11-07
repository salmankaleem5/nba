from util.data import TrackingStats
from util.reddit import print_reddit_table

trackingStats = TrackingStats()

currentYear = trackingStats.get_data({'Season': '2017-18', 'PerMode': 'Totals', 'PtMeasureType': 'Possessions'})
lastYear = trackingStats.get_data({'Season': '2016-17', 'PerMode': 'Totals', 'PtMeasureType': 'Possessions'})
currentYear['YEAR'] = '2017-18'
lastYear['YEAR'] = '2016-17'

merge = currentYear.append(lastYear)
merge['TOP_PER_MIN'] = (merge['TIME_OF_POSS'] / merge['MIN']) * 100

westbrook = merge[merge.PLAYER_NAME == 'Carmelo Anthony']
print_reddit_table(westbrook, ['YEAR', 'MIN', 'TIME_OF_POSS', 'TOP_PER_MIN'])