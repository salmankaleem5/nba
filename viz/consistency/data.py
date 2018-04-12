from util.consistency import get_data_for_year
import json

data = get_data_for_year('2017-18')

data.to_json('./data/data.json', orient='records')

# with open('./data/data.json', 'w') as fp:
#     json.dump(data, fp)
