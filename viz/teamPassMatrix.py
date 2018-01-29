from util.nba_stats import PlayerPassDashboard, GeneralPlayerStats
import pandas as pd

import plotly.plotly as py
import plotly.graph_objs as go

pass_ep = PlayerPassDashboard()
general_ep = GeneralPlayerStats()

season = '2017-18'
team_id = '1610612740'
team_name = 'Pelicans'
per_mode = 'PerGame'
games_filter = 30
minutes_filter = 25
data_override = False

general_df = general_ep.get_data({'Season': season, 'PerMode': per_mode, 'MeasureType': 'Base', 'TeamID': team_id},
                                 override_file=data_override)
general_df = general_df[general_df['GP'] >= games_filter]
general_df = general_df[general_df['MIN'] >= minutes_filter]

general_df = general_df.sort_values(by='MIN', ascending=False)

players = general_df['PLAYER_ID'].tolist()

df = pd.DataFrame()

for ix, player in general_df.iterrows():
    player_pass_df = pass_ep.get_data(
        {'Season': season, 'PerMode': per_mode, 'PlayerID': player.PLAYER_ID, 'TeamID': player.TEAM_ID},
        override_file=data_override)

    if len(player_pass_df) == 0:
        continue

    player_pass_df = player_pass_df[player_pass_df['PASS_TEAMMATE_PLAYER_ID'].isin(players)]

    player_pass_df['EFG'] = round(
        ((player_pass_df['FG2M'] + player_pass_df['FG3M'] * 1.5) / player_pass_df['FGA']) * 100, 2)

    player_pass_df = player_pass_df[
        ['PLAYER_NAME_LAST_FIRST', 'PLAYER_ID', 'PASS_TO', 'PASS_TEAMMATE_PLAYER_ID', 'PASS', 'AST', 'EFG']]

    player_name = player_pass_df.iloc[0]['PLAYER_NAME_LAST_FIRST']
    player_pass_df.loc[-1] = [player_name, player.PLAYER_ID, player_name, player.PLAYER_ID, 0, 0, 50]
    player_pass_df = player_pass_df.rename(columns={'PLAYER_NAME_LAST_FIRST': 'FROM', 'PASS_TO': 'TO'})

    df = df.append(player_pass_df)


df['INFO'] = 'PASS: ' + df['PASS'].astype(str) + '<br />' + 'AST: ' + df['AST'].astype(str) + '<br />' + 'EFG%: ' + df[
    'EFG'].astype(str)

df = df.merge(general_df[['PLAYER_ID', 'MIN']], on=['PLAYER_ID'])
df = df.rename(columns={'MIN': 'FROM_MIN'})

df = df.merge(general_df[['PLAYER_ID', 'MIN']], left_on=['PASS_TEAMMATE_PLAYER_ID'], right_on=['PLAYER_ID'])
df = df.rename(columns={'MIN': 'TO_MIN'})

df = df.sort_values(by=['FROM_MIN', 'TO_MIN'], ascending=False)

trace = go.Scatter(
    x=df['FROM'],
    y=df['TO'],
    text=df['INFO'],
    mode='markers',
    marker=dict(
        size=df['AST'] * 30,
        color=df['EFG']
    )
)

layout = go.Layout(
    title=team_name + ' Passing',
    xaxis=dict(
        title='Passer'
    ),
    yaxis=dict(
        title='Receiver'
    ),
    showlegend=False
)

fig = go.Figure(data=[trace], layout=layout)
py.plot(fig, filename=team_name + ' Passing')
