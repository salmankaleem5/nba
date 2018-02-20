import pandas as pd
from util.nba_stats import Standings

# Import Data
schedule = pd.read_csv('./schedule.csv')
remaining_schedule = schedule[schedule['Home_Pts'].isnull()]

standings = Standings().get_data({})
standings['Team'] = standings['TeamCity'].map(str) + ' ' + standings['TeamName'].map(str)
standings = standings[['Team', 'Conference', 'WINS', 'LOSSES', 'WinPCT', 'PlayoffRank']]

# Standings uses LA Clippers / Schedule uses Los Angeles Clippers: make consistent
standings.set_value(16, 'Team', 'Los Angeles Clippers')

# Determine win% needed to finish .500
standings['500'] = (41 - standings['WINS']) / (82 - standings['WINS'] - standings['LOSSES'])

# Define team categories
team_categories = {
    'Pelicans': standings['Team'] == 'New Orleans Pelicans',
    'Top': (standings['500'] <= 1 / 3) & (standings['Conference'] == 'West'),
    'HopeIn': (standings['500'] > 1 / 3) & (standings['500'] <= 2 / 3) & (standings['PlayoffRank'] <= 8) & (
                standings['Conference'] == 'West'),
    'HopeOut': (standings['500'] > 1 / 3) & (standings['500'] <= 2 / 3) & (standings['PlayoffRank'] > 8) & (
                standings['Conference'] == 'West'),
    'Bottom': (standings['500'] > 2 / 3) & (standings['Conference'] == 'West'),
    'East': standings['Conference'] == 'East'
}

# Set Category Column according to defined conditions
standings['Category'] = ''
for c in team_categories:
    standings.loc[team_categories[c], 'Category'] = c


# Convert standings dataframe to dictionary for easier lookup
standings_dict = standings.set_index('Team').to_dict('index')

# Create dict of game categories from team categories
game_categories = {}
for tc1 in team_categories:
    for tc2 in team_categories:
        if (tc2 + ' vs ' + tc1) not in game_categories:
            game_categories[tc1 + ' vs ' + tc2] = 0

# Iterate through schedule, assign each game a category, and add to categories count
schedule_category_column = []
for ix, game in remaining_schedule.iterrows():
    home_category = standings_dict[game['Home']]['Category']
    visitor_category = standings_dict[game['Visitor']]['Category']

    game_category = home_category + ' vs ' + visitor_category
    game_category = game_category if game_category in game_categories else visitor_category + ' vs ' + home_category

    game_categories[game_category] += 1
    schedule_category_column.append(game_category)

remaining_schedule['Category'] = pd.Series(schedule_category_column)

# Create matrix of game counts by team categories
df = pd.DataFrame(columns=['OPP'] + list(team_categories.keys()))
df['OPP'] = list(team_categories.keys())
df = df.fillna(0)

for gc in game_categories:
    gc1, gc2 = gc.split(' vs ')
    df.loc[df['OPP'] == gc1, gc2] += game_categories[gc]
    df.loc[df['OPP'] == gc2, gc1] += game_categories[gc]

df.to_csv('game_counts.csv')
remaining_schedule.to_csv('categorized_schedule.csv')

