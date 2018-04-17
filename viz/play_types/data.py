from util.data_scrappers.nba_stats import SynergyPlayerStats, SynergyTeamStats, param_list
import json
import pandas as pd


def get_stats_for_players():
    pt_ep = SynergyPlayerStats()

    data = {}
    for pt in param_list['category']['choices']:
        pt_df = pt_ep.get_data({'category': pt}, override_file=False).fillna(0)
        pt_df = pt_df[pt_df['Poss'] >= 50]
        pt_df['Player'] = pt_df['PlayerFirstName'] + ' ' + pt_df['PlayerLastName']
        pt_df = pt_df[['Player', 'PossG', 'PPP']]
        data[pt] = pt_df.to_dict(orient='records')

    with open('./players/data/data.json', 'w') as fp:
        json.dump(data, fp)


def get_stats_for_teams():
    pt_ep = SynergyTeamStats()

    data = {}
    for pt in param_list['category']['choices']:
        pt_df = pd.DataFrame()
        for side in ['offensive', 'defensive']:
            side_df = pt_ep.get_data({'category': pt, 'names': side}, override_file=False).fillna(0)
            side_df['Team'] = side_df["TeamNameAbbreviation"]
            side_df = side_df[['Team', 'PossG', 'PPP']]
            side_df['Side'] = side
            pt_df = pt_df.append(side_df)
        data[pt] = pt_df.to_dict(orient='records')

    with open('./team_matchups/data/data.json', 'w') as fp:
        json.dump(data, fp)


# get_stats_for_players()
get_stats_for_teams()