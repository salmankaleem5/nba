from util.shot_chart import nest_data_for_all_players_season
from util.data_scrappers.nba_stats import GeneralPlayerStats
from util.format import get_year_string
import requests
import shutil
import json
import pandas as pd


def get_all_players_season(season):
    df = get_shots_for_all_players_season(season)
    df.to_json('./data/shots.json', orient='records')


def get_all_season_player(player_name, year_range):
    df = pd.DataFrame()
    for year in year_range:
        year_string = get_year_string(year)
        year_df = get_shots_for_player_season(player_name, year_string)
        year_df['player'] = year_df['player'] + ' ' + year_string
        df = df.append(year_df)
    df.to_json('./data/shots.json', orient='records')


def get_player_pictures(season):
    players = GeneralPlayerStats().get_data({'Season': season})['PLAYER_ID'].unique()
    image_url = 'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/1610612740/2017/260x190/{}.png'
    image_file_location = './img/{}.svg'
    for p in players:
        player_url = image_url.format(p)
        player_file_location = image_file_location.format(p)
        response = requests.get(player_url, stream=True)
        with open(player_file_location, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response


data = nest_data_for_all_players_season('2017-18', fga_filter=1000)
with open('./data/shots.json', 'w') as fp:
    json.dump(data, fp)
