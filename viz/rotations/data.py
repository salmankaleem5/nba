from util.rotations import get_viz_data_for_team_season

df = get_viz_data_for_team_season('PHI')
df.to_csv('./data.csv')
