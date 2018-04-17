from util.data_scrappers.nba_stats import SynergyPlayerStats, SynergyTeamStats, param_list
from util.data import write_dict_to_json_file
import pandas as pd


def get_stats_for_players_season(season):
    pt_ep = SynergyPlayerStats()

    data = {}
    for pt in param_list['category']['choices']:
        pt_df = pt_ep.get_data({'category': pt, 'season': season}, override_file=False).fillna(0)
        pt_df = pt_df[pt_df['Poss'] >= 50]
        pt_df['Player'] = pt_df['PlayerFirstName'] + ' ' + pt_df['PlayerLastName']
        pt_df = pt_df[['Player', 'PossG', 'PPP']]
        pt_df['Year'] = season
        data[pt] = pt_df.to_dict(orient='records')

    return data


def get_stats_for_teams_season(season):
    pt_ep = SynergyTeamStats()

    data = {}
    for pt in param_list['category']['choices']:
        pt_df = pd.DataFrame()
        for side in ['offensive', 'defensive']:
            side_df = pt_ep.get_data({'category': pt, 'names': side, 'season': season}, override_file=False).fillna(0)
            side_df['Team'] = side_df["TeamNameAbbreviation"]
            side_df = side_df[['Team', 'PossG', 'PPP']]
            side_df['Year'] = season
            side_df['Side'] = side
            pt_df = pt_df.append(side_df)
        data[pt] = pt_df.to_dict(orient='records')

    return data


def get_stats_for_players_all_season():
    all_year_stats = {}
    for pt in param_list['category']['choices']:
        all_year_stats[pt] = []
    for year in range(2015, 2018):
        year_stats = get_stats_for_players_season(str(year))
        for pt in param_list['category']['choices']:
            all_year_stats[pt].extend(year_stats[pt])
    return all_year_stats


def get_stats_for_teams_all_seasons():
    all_year_stats = {}
    for pt in param_list['category']['choices']:
        all_year_stats[pt] = []
    for year in range(2015, 2018):
        year_stats = get_stats_for_teams_season(str(year))
        for pt in param_list['category']['choices']:
            all_year_stats[pt].extend(year_stats[pt])
    return all_year_stats


data = get_stats_for_players_all_season()
write_dict_to_json_file(data, './players/data/data.json')
