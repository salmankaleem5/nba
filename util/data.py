import requests
from requests import Request
import pandas as pd
from dateutil.parser import parse
from fuzzywuzzy import process

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
                            'Per36', 'Per40', 'Per48']},
    'PlayerOrTeam': {'type': 'Enum', 'choices': ['Player', 'Team']},
    'PtMeasureType': {'type': 'Enum',
                      'choices': ['Drives', 'Defense', 'CatchShoot', 'Passing', 'Possessions', 'PullUpShot',
                                  'Rebounding', 'Efficiency', 'SpeedDistance', 'ElbowTouch', 'PostTouch', 'PaintTouch']}
}


def get_year_string(year):
    return str(year) + "-" + str(year + 1)[2:4]


class EndPoint:
    base_url = ''
    default_params = {}
    params = {}

    def __init__(self, passed_params):
        self.params = self.set_params(passed_params)
        self.check_params()

    def check_params(self):
        for key, value in self.params.items():
            if key in param_list:
                p = param_list[key]
                if p['type'] == 'Enum' and value not in p['choices']:
                    suggestions = process.extract(value, p['choices'], limit=3)
                    raise ValueError(
                        str(value) + " is not a valid value for " + str(key) + ". Did you mean: " + str(suggestions))
                if p['type'] == 'Date' and value != '':
                    parse(value)

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

    def get_data(self):
        r = requests.post(self.base_url, data=self.params, headers=request_headers)
        print(str(r.status_code) + ': ' + str(r.url))
        data = r.json()['resultSets'][0]
        headers = data['headers']
        rows = data['rowSet']
        data_dict = [dict(zip(headers, row)) for row in rows]
        return pd.DataFrame(data_dict)


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


class SynergyPlayerStats(EndPoint):
    base_url = 'https://stats-prod.nba.com/wp-json/statscms/v1/synergy/player/?'
    default_params = {'category': 'PRRollman',
                      'limit': '500',
                      'names': 'offensive',
                      'q': '2511761',
                      'season': '2016',
                      'seasonType': 'Reg'}
    synergy_request_headers = {
        'Host': 'stats-prod.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'http://stats.nba.com/players/roll-man/',
        'Origin': 'http://stats.nba.com'
    }

    def get_data(self):
        r = Request('POST', self.base_url, params=self.params, headers=self.synergy_request_headers)
        pretty_print_POST(r.prepare())
        data = r.json()['results']
        # headers = data[0].keys()
        # rows = [0] * len(data)
        # for i in range(len(data)):
        #     rows[i] = data[i].values()
        # data_dict = [dict(zip(headers, row)) for row in rows]
        # return pd.DataFrame(data_dict)


def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


SynergyPlayerStats({}).get_data()
