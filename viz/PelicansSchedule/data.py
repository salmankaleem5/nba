import pandas as pd
import datetime
from util.nba_stats import Standings

# Import Data
schedule = pd.read_csv('./schedule.csv')

current_date = datetime.date.today()
schedule['Date'] = schedule['Date'].map(lambda x:
                                        x.split(' ')[1] + '-' +
                                        (x.split(' ')[2] if len(x.split(' ')[2]) == 2 else '0' + x.split(' ')[2]) +
                                        '-' + x.split(' ')[3])

schedule['Date'] = pd.to_datetime(schedule['Date'], infer_datetime_format=True)
remaining_schedule = schedule[schedule['Date'] >= current_date]

standings = Standings().get_data({})
standings['Team'] = standings['TeamCity'].map(str) + ' ' + standings['TeamName'].map(str)
standings = standings[['Team', 'Conference', 'WINS', 'LOSSES', 'WinPCT', 'PlayoffRank']]

# Standings uses LA Clippers / Schedule uses Los Angeles Clippers: make consistent
standings.set_value(16, 'Team', 'Los Angeles Clippers')

teams = standings[
    (standings['Conference'] == 'West') &
    (standings['PlayoffRank'] >= 3) &
    (standings['PlayoffRank'] <= 10)]['Team'].tolist()


data = []
for team1 in teams:
    team_df = remaining_schedule[
        (remaining_schedule['Home'] == team1) | (remaining_schedule['Visitor'] == team1)
    ]

    team_data = {'Team': team1}

    for team2 in teams:
        if team1 != team2:
            matchup_df = team_df[
                (team_df['Home'] == team2) | (team_df['Visitor'] == team2)
            ]
            team_data[team2] = len(matchup_df)
        else:
            team_data[team2] = 0

    data.append(team_data)

head_to_head_df = pd.DataFrame(data)[['Team'] + teams]

