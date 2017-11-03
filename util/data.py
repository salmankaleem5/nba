import requests
import pandas as pd
import hashlib
import os
import platform
from dateutil.parser import parse
from fuzzywuzzy import process

if "Windows" in platform.platform():
    data_dir = 'C:\\data\\nba\\'
else:
    data_dir = '/home/patrick/Data/nba/'

request_headers = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
    'Cookie': '_ga=GA1.2.1910425825.1503411323; s_fid=77702B4521AF9F5D-27C7181E5E3CC3A4; ug=59a6c4cf03229f0a3c26e13'
              'a1b015b2b; s_vi=[CS]v1|2CD36268050316EB-60001184600029D9[CE]; __gads=ID=390e9947dd413dc1:T=150410158'
              '4:S=ALNI_Mae1yHotZvFo066PX75ZYAUGvQlVA; s_cc=true; s_sq=%5B%5BB%5D%5D',
    'DNT': '1'
}

param_list = {
    'DateFrom': {'type': 'Date'},
    'DateTo': {'type': 'Date'},
    'MeasureType': {'type': 'Enum', 'choices': ['Base', 'Advanced', 'Misc', 'Scoring', 'Usage', 'Opponent', 'Defense']},
    'SeasonType': {'type': 'Enum', 'choices': ['Pre Season', 'Regular Season', 'Playoffs', 'All Star']},
    'PerMode': {'type': 'Enum',
                'choices': ['PerGame', 'Per100Possessions', 'PerPossession', 'Per100Plays', 'PerPlay', 'PerMinute',
                            'Per36', 'Per40', 'Per48', 'Totals']},
    'PlayerOrTeam': {'type': 'Enum', 'choices': ['Player', 'Team', 'P', 'T']},
    'PtMeasureType': {'type': 'Enum',
                      'choices': ['Drives', 'Defense', 'CatchShoot', 'Passing', 'Possessions', 'PullUpShot',
                                  'Rebounding', 'Efficiency', 'SpeedDistance', 'ElbowTouch', 'PostTouch',
                                  'PaintTouch']},
    'DistanceRange': {'type': 'Enum', 'choices': ['By Zone', '5ft Range', '8ft Range']}
}


def get_year_string(year):
    return str(year) + "-" + str(year + 1)[2:4]


def file_check(file_path):
    split_path = file_path.split('/')
    current_path = ''
    for p in range(0, len(split_path) - 1):
        current_path += split_path[p] + '/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
    return os.path.isfile(file_path)


def check_params(params):
    for key, value in params.items():
        if key in param_list:
            p = param_list[key]
            if p['type'] == 'Enum' and value not in p['choices']:
                suggestions = process.extract(value, p['choices'], limit=3)
                raise ValueError(
                    str(value) + " is not a valid value for " + str(key) + ". Did you mean: " + str(suggestions))
            if p['type'] == 'Date' and value != '':
                parse(value)


def get_full_url(base, params):
    s = base + '?'
    for param in params:
        s += param + '=' + params[param] + '&'
    return s


class EndPoint:
    base_url = ''
    default_params = {}
    season_year_param = 'Season'
    index = 0

    def __init__(self):
        None

    def set_params(self, passed_params):
        params = self.default_params
        for key, value in passed_params.items():
            if key in self.default_params:
                params[key] = value
            else:
                suggestions = process.extract(key, self.default_params.keys(), limit=3)
                raise ValueError(
                    str(key) + " is not a valid parameter for this endpoint. Did you mean: " + str(suggestions))
        return params

    def get_data(self, passed_params, override_file=False):
        params = self.set_params(passed_params)
        check_params(params)

        param_string = str(params).encode('utf-8')
        param_hash = hashlib.sha1(param_string).hexdigest()
        endpoint_name = self.base_url.split('/')[-1]

        file_path = data_dir + endpoint_name + '/' + str(param_hash) + '.csv'

        if (not file_check(file_path)) or override_file:
            print(get_full_url(self.base_url, params))
            r = requests.post(self.base_url, data=params, headers=request_headers)
            if r.status_code == 200:
                data = r.json()['resultSets'][self.index]
                headers = data['headers']
                rows = data['rowSet']
                data_dict = [dict(zip(headers, row)) for row in rows]
                df = pd.DataFrame(data_dict)
                df.to_csv(file_path)
                return df
            else:
                raise ConnectionError(str(r.status_code) + ': ' + str(r.reason))
        else:
            print(file_path)
            return pd.read_csv(file_path)

    def get_data_for_year_range(self, year_range, other_params):
        df = pd.DataFrame()
        for year in year_range:
            year_string = get_year_string(year)

            other_params[self.season_year_param] = year_string

            year_df = self.get_data(other_params)
            year_df['YEAR'] = year_string
            df = df.append(year_df)
        return df


class GeneralPlayerStats(EndPoint):
    base_url = 'http://stats.nba.com/stats/leaguedashplayerstats'
    default_params = {
        'College': '',
        'Conference': '',
        'Country': '',
        'DateFrom': '',
        'DateTo': '',
        'Division': '',
        'DraftPick': '',
        'DraftYear': '',
        'GameScope': '',
        'GameSegment': '',
        'Height': '',
        'LastNGames': '0',
        'LeagueID': '00',
        'Location': '',
        'MeasureType': 'Base',
        'Month': '0',
        'OpponentTeamID': '0',
        'Outcome': '',
        'PORound': '0',
        'PaceAdjust': 'N',
        'PerMode': 'PerGame',
        'Period': '0',
        'PlayerExperience': '',
        'PlayerPosition': '',
        'PlusMinus': 'N',
        'Rank': 'N',
        'Season': '2016-17',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'ShotClockRange': '',
        'StarterBench': '',
        'TeamID': '0',
        'VsConference': '',
        'VsDivision': '',
        'Weight': ''
    }


class GeneralTeamStats(EndPoint):
    base_url = 'http://stats.nba.com/stats/leaguedashteamstats'
    default_params = {
        'Conference': '',
        'DateFrom': '',
        'DateTo': '',
        'Division': '',
        'GameScope': '',
        'GameSegment': '',
        'LastNGames': '0',
        'LeagueID': '00',
        'Location': '',
        'MeasureType': 'Base',
        'Month': '0',
        'OpponentTeamID': '0',
        'Outcome': '',
        'PORound': '0',
        'PaceAdjust': 'N',
        'PerMode': 'PerGame',
        'Period': '0',
        'PlayerExperience': '',
        'PlayerPosition': '',
        'PlusMinus': 'N',
        'Rank': 'N',
        'Season': '2016-17',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'ShotClockRange': '',
        'StarterBench': '',
        'TeamID': '0',
        'VsConference': '',
        'VsDivision': '',
    }


class TrackingStats(EndPoint):
    base_url = 'http://stats.nba.com/stats/leaguedashptstats'
    default_params = {
        'Conference': '',
        'Country': '',
        'DateFrom': '',
        'DateTo': '',
        'Division': '',
        'DraftPick': '',
        'DraftYear': '',
        'GameScope': '',
        'Height': '',
        'LastNGames': '0',
        'LeagueID': '00',
        'Location': '',
        'Month': '0',
        'OpponentTeamID': '0',
        'Outcome': '',
        'PORound': '0',
        'PerMode': 'PerGame',
        'PlayerExperience': '',
        'PlayerOrTeam': 'Player',
        'PlayerPosition': '',
        'PtMeasureType': 'Drives',
        'Season': '2016-17',
        'SeasonSegment ': '',
        'SeasonType': 'Regular Season',
        'StarterBench': '',
        'TeamID': '0',
        'VsConference ': '',
        'VsDivision ': '',
        'Weight': ''
    }


class HustleStats(EndPoint):
    base_url = 'https://stats.nba.com/stats/leaguehustlestatsplayer'
    default_params = {
        'College': '',
        'Conference': '',
        'Country': '',
        'DateFrom': '',
        'DateTo': '',
        'Division': '',
        'DraftPick': '',
        'DraftYear': '',
        'GameScope': '',
        'Height': '',
        'LastNGames': '0',
        '&LeagueID': '00',
        'Location': '',
        'Month': '0',
        'OpponentTeamID': '0',
        'Outcome': '',
        'PORound': '0',
        'PaceAdjust': 'N',
        'PerMode': 'PerGame',
        'PlayerExperience': '',
        'PlayerPosition': '',
        'PlusMinus': 'N',
        'Rank': 'N',
        'Season': '2017-18',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'TeamID': '0',
        'VsConference': '',
        'VsDivision': '',
        'Weight': ''
    }


class PlayerBios(EndPoint):
    base_url = 'http://stats.nba.com/stats/leaguedashplayerbiostats'
    default_params = {
        'College': '',
        'Conference': '',
        'Country': '',
        'DateFrom': '',
        'DateTo': '',
        'Division': '',
        'DraftPick': '',
        'DraftYear': '',
        'GameScope': '',
        'GameSegment': '',
        'Height': '',
        'LastNGames': '0',
        'LeagueID': '00',
        'Location': '',
        'Month': '0',
        'OpponentTeamID': '0',
        'Outcome': '',
        'PORound': '0',
        'PerMode': 'PerGame',
        'Period': '0',
        'PlayerExperience': '',
        'PlayerPosition': '',
        'Season': '2016-17',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'ShotClockRange': '',
        'StarterBench': '',
        'TeamID': '0',
        'VsConference': '',
        'VsDivision': '',
        'Weight': ''
    }


class GameLogs(EndPoint):
    base_url = 'http://stats.nba.com/stats/leaguegamelog'
    default_params = {
        'Counter': '1000',
        'DateFrom': '',
        'DateTo': '',
        'Direction': 'DESC',
        'LeagueID': '00',
        'PlayerOrTeam': 'P',
        'Season': '2017-18',
        'SeasonType': 'Regular Season',
        'Sorter': 'DATE'
    }


class TeamShootingStats(EndPoint):
    base_url = 'http://stats.nba.com/stats/leaguedashteamshotlocations'
    default_params = {
        'Conference': '',
        'DateFrom': '',
        'DateTo': '',
        'Division': '',
        'DistanceRange': 'By Zone',
        'GameScope': '',
        'GameSegment': '',
        'LastNGames': '0',
        'LeagueID': '00',
        'Location': '',
        'MeasureType': 'Base',
        'Month': '0',
        'OpponentTeamID': '0',
        'Outcome': '',
        'PORound': '0',
        'PaceAdjust': 'N',
        'PerMode': 'Totals',
        'Period': '0',
        'PlayerExperience': '',
        'PlayerPosition': '',
        'PlusMinus': 'N',
        'Rank': 'N',
        'Season': '2017-18',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'ShotClockRange': '',
        'StarterBench': '',
        'TeamID': '0',
        'VsConference': '',
        'VsDivision': '',
    }
    index = 1

    def get_data(self, passed_params, override_file=False):
        params = self.set_params(passed_params)
        check_params(params)

        param_string = str(params).encode('utf-8')
        param_hash = hashlib.sha1(param_string).hexdigest()
        endpoint_name = self.base_url.split('/')[-1]

        file_path = data_dir + endpoint_name + '/' + str(param_hash) + '.csv'

        if (not file_check(file_path)) or override_file:
            r = requests.post(self.base_url, data=params, headers=request_headers)
            print(str(r.status_code) + ': ' + str(self.base_url))
            data = r.json()['resultSets']

            headers = ['TEAM_ID', 'TEAM_NAME']
            shot_zones = data['headers'][0]['columnNames']
            for sz in shot_zones:
                headers.append(sz + '_FGM')
                headers.append(sz + '_FGA')
                headers.append(sz + '_FG_PCT')

            rows = data['rowSet']
            data_dict = [dict(zip(headers, row)) for row in rows]
            df = pd.DataFrame(data_dict)
            df.to_csv(file_path)
            return df
        else:
            print(file_path)
            return pd.read_csv(file_path)

    def get_zones(self, zone_type):
        if zone_type == 'By Zone':
            return ['Restricted Area', 'In The Paint (Non-RA)', 'Mid-Range', 'Left Corner 3', 'Right Corner 3',
                    'Above the Break 3', 'Backcourt']
        elif zone_type == '5ft Range':
            return ['Less Than 5ft', '5-9 ft', '10-14 ft', '15-19 ft', '20-24 ft', '25-29 ft', '30-34 ft', '35-39 ft',
                    '40+ ft']
        elif zone_type == '8ft Range':
            return ['Less Than 8ft', '8-16 ft', '16-24ft', '24+ ft', 'Back Court Shot']
        else:
            check_params({'DistanceRange': zone_type})


class OnOffSummary(EndPoint):
    base_url = 'http://stats.nba.com/stats/teamplayeronoffsummary'
    default_params = {
        'DateFrom': '',
        'DateTo': '',
        'GameSegment': '',
        'LastNGames': '0',
        'LeagueID': '00',
        'Location': '',
        'MeasureType': 'Base',
        'Month': '0',
        'OpponentTeamID': '0',
        'Outcome': '',
        'PaceAdjust': 'N',
        'PerMode': 'Totals',
        'Period': '0',
        'PlusMinus': 'N',
        'Rank': 'N',
        'Season': '2017-18',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'TeamID': '0',
        'VsConference': '',
        'VsDivision': '',
    }

    def get_data(self, passed_params, override_file=False):
        params = self.set_params(passed_params)
        check_params(params)

        param_string = str(params).encode('utf-8')
        param_hash = hashlib.sha1(param_string).hexdigest()
        endpoint_name = self.base_url.split('/')[-1]

        file_path = data_dir + endpoint_name + '/' + str(param_hash) + '.csv'

        if (not file_check(file_path)) or override_file:
            r = requests.post(self.base_url, data=params, headers=request_headers)
            print(str(r.status_code) + ': ' + str(self.base_url))
            data = r.json()['resultSets'][1]
            headers = ['GROUP_SET_ON', 'TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'VS_PLAYER_ID', 'VS_PLAYER_NAME',
                       'COURT_STATUS_ON', 'GP_ON', 'MIN_ON', 'PLUS_MINUS_ON', 'OFF_RATING_ON', 'DEF_RATING_ON',
                       'NET_RATING_ON']
            rows = data['rowSet']
            data_dict = [dict(zip(headers, row)) for row in rows]
            on_df = pd.DataFrame(data_dict)
            data = r.json()['resultSets'][2]
            headers = ['GROUP_SET_OFF', 'TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'VS_PLAYER_ID', 'VS_PLAYER_NAME',
                       'COURT_STATUS_OFF', 'GP_OFF', 'MIN_OFF', 'PLUS_MINUS_OFF', 'OFF_RATING_OFF', 'DEF_RATING_OFF',
                       'NET_RATING_OFF']
            rows = data['rowSet']
            data_dict = [dict(zip(headers, row)) for row in rows]
            off_df = pd.DataFrame(data_dict)
            df = pd.merge(on_df, off_df,
                          on=['TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'VS_PLAYER_ID', 'VS_PLAYER_NAME'])
            df.to_csv(file_path)
            return df
        else:
            print(file_path)
            return pd.read_csv(file_path)


class SynergyPlayerStats(EndPoint):
    base_url = 'https://stats-prod.nba.com/wp-json/statscms/v1/synergy/player/'
    default_params = {'category': 'PRRollman',
                      'limit': '500',
                      'names': 'offensive',
                      'q': '2511761',
                      'season': '2016',
                      'seasonType': 'Reg'}
    synergy_request_headers = {
        'Host': 'dev.stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'http://stats.nba.com/players/roll-man/',
        'Origin': 'http://stats.nba.com',
        'DNT': '1',
        'Connection': 'keep-alive'
    }

    def get_data(self, passed_params, override_file=False):
        params = self.set_params(passed_params)
        check_params(params)

        param_string = str(params).encode('utf-8')
        param_hash = hashlib.sha1(param_string).hexdigest()
        endpoint_name = self.base_url.split('/')[-1]

        file_path = data_dir + endpoint_name + '/' + str(param_hash) + '.csv'

        if (not file_check(file_path)) or override_file:
            r = requests.get(self.base_url, data=params, headers=request_headers, allow_redirects=True)
            get_full_url(self.base_url, params)
            print(r.headers)
            data = r.json()['results']
            headers = data[0].keys()
            rows = [0] * len(data)
            for i in range(len(data)):
                rows[i] = data[i].values()
            data_dict = [dict(zip(headers, row)) for row in rows]
            df = pd.DataFrame(data_dict)
            df.to_csv(file_path)
            return df
        else:
            print(file_path)
            return pd.read_csv(file_path)
