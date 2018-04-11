from util.rotations import get_viz_data_for_team_season, get_viz_data_for_team_game_set, \
    get_game_ids_for_team_with_starters, get_most_common_starters_for_team_season

# df = get_viz_data_for_team_season('NOP', '2017-18')

# get_most_common_starters_for_team_season('NOP', '2017-18')
games = get_game_ids_for_team_with_starters(
    ['Anthony Davis', "E'Twaun Moore", 'Jrue Holiday', 'Nikola Mirotic', 'Rajon Rondo'], 'NOP', '2017-18')
df = get_viz_data_for_team_game_set('NOP', games, '2017-18')
None
# df.to_json('./rotations.json', orient='records')