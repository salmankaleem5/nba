from util.shot_chart.shot_chart import get_shots_for_player_season


player_name = 'Anthony Davis'
year = '2017-18'

df = get_shots_for_player_season(player_name, year)
df.to_json('./data/shots.json', orient='records')
