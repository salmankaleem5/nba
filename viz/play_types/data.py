from util.data_scrappers.nba_stats import SynergyPlayerStats, param_list
import json

pt_ep = SynergyPlayerStats()

data = {}
for pt in param_list['category']['choices']:
    pt_df = pt_ep.get_data({'category': pt}).fillna(0)
    pt_df = pt_df[['PlayerFirstName', 'PlayerLastName', 'Time', 'PPP']]
    data[pt] = pt_df.to_dict(orient='records')

with open('./data/data.json', 'w') as fp:
    json.dump(data, fp)
