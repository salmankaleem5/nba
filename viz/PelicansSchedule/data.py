import pandas as pd
from util.nba_stats import Standings

schedule = pd.read_csv('./schedule.csv')
remaining_schedule = schedule[schedule['Home_Pts'].isnull()]

standings = Standings().get_data({})
standings['Team'] = standings['TeamCity'].map(str) + ' ' + standings['TeamName'].map(str)
standings = standings[['Team', 'Conference', 'WINS', 'LOSSES', 'WinPCT', 'PlayoffRank']]

standings['500'] = (41 - standings['WINS']) / (82 - standings['WINS'] - standings['LOSSES'])

standings['Cat'] = ''
standings.set_value(16, 'Team', 'Los Angeles Clippers')

standings_dict = standings.set_index('Team').to_dict('index')

for team in standings_dict:
    if team == 'New Orleans Pelicans':
        standings_dict[team]['Cat'] = 'Pelicans'
    elif standings_dict[team]['Conference'] == 'East':
        standings_dict[team]['Cat'] = 'East'
    elif standings_dict[team]['500'] < 1/3:
        standings_dict[team]['Cat'] = 'Top'
    elif 2/3 > standings_dict[team]['500'] > 1/3:
        if standings_dict[team]['PlayoffRank'] <= 8:
            standings_dict[team]['Cat'] = 'HopeIn'
        else:
            standings_dict[team]['Cat'] = 'HopeOut'
    else:
        standings_dict[team]['Cat'] = 'Bot'


types = ['Pelicans', 'HopeOut', 'HopeIn', 'Top', 'Bot', 'East']
games = {}
for t1 in types:
    for t2 in types:
        games[t1 + ' vs ' + t2] = 0

gt = []
for ix, game in remaining_schedule.iterrows():
    game_type = sorted([standings_dict[game['Home']]['Cat'], standings_dict[game['Visitor']]['Cat']])
    game_type = game_type[0] + ' vs ' + game_type[1]
    gt.append(game_type)
    if game_type in games:
        games[game_type] += 1

remaining_schedule['Type'] = gt

df = pd.DataFrame(columns=['OPP'] + types)
df['OPP'] = types

for t1 in types:
    type_data = []
    for t2 in types:
        type_array = sorted([t1, t2])
        game_type = type_array[0] + ' vs ' + type_array[1]
        num_games = games[game_type]
        type_data.append(num_games)
    df[t1] = type_data

df.to_csv('data.csv')
