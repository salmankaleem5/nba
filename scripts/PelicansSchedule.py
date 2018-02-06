import pandas as pd
from util.nba_stats import Standings

schedule = pd.read_csv('C:\data\schedule.csv')
remaining_schedule = schedule[schedule['Home_Pts'].isnull()]

standings = Standings().get_data({})
standings['Team'] = standings['TeamCity'].map(str) + ' ' + standings['TeamName'].map(str)
standings = standings[['Team', 'Conference', 'WINS', 'LOSSES', 'WinPCT', 'PlayoffRank']]

standings['500'] = (41 - standings['WINS']) / (82 - standings['WINS'] - standings['LOSSES'])

standings['Cat'] = ''
standings.set_value(17, 'Team', 'Los Angeles Clippers')

standings = standings.set_index('Team').to_dict('index')

for team in standings:
    if team == 'New Orleans Pelicans':
        standings[team]['Cat'] = 'Pelicans'
    elif standings[team]['Conference'] == 'East':
        standings[team]['Cat'] = 'East'
    elif standings[team]['500'] < 1/3:
        standings[team]['Cat'] = 'Top'
    elif 2/3 > standings[team]['500'] > 1/3:
        if standings[team]['PlayoffRank'] <= 8:
            standings[team]['Cat'] = 'HopeIn'
        else:
            standings[team]['Cat'] = 'HopeOut'
    else:
        standings[team]['Cat'] = 'Bot'


types = sorted(['Pelicans', 'East', 'Top', 'HopeIn', 'HopeOut', 'Bot'])
games = {}
for t1 in types:
    for t2 in types:
        games[t1 + ' vs ' + t2] = 0

gt = []
for ix, game in remaining_schedule.iterrows():
    game_type = sorted([standings[game['Home']]['Cat'], standings[game['Visitor']]['Cat']])
    game_type = game_type[0] + ' vs ' + game_type[1]
    gt.append(game_type)
    if game_type in games:
        games[game_type] += 1

remaining_schedule['Game Type'] = gt

data = []
for game_type in games:
    t1 = game_type.split(' vs ')[0]
    t2 = game_type.split(' vs ')[1]
    val = games[game_type]
    data.append({
        'teamA': t1,
        'teamB': t2,
        'games': val
    })

df = pd.DataFrame(data)

