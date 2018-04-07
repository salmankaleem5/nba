import requests
import pandas as pd
import hashlib
from dateutil.parser import parse
from fuzzywuzzy import process

from util.data import data_dir, file_check
from util.format import get_year_string

request_headers = {
    'Host': 'stats.nba.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0)' +
                  ' Gecko/20100101 Firefox/55.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true',
    'Cookie': '_ga=GA1.2.1910425825.1503411323;' +
              ' s_fid=77702B4521AF9F5D-27C7181E5E3CC3A4;' +
              ' ug=59a6c4cf03229f0a3c26e13' +
              'a1b015b2b; s_vi=[CS]v1|2CD36268050316EB-60001184600029D9[CE];' +
              ' __gads=ID=390e9947dd413dc1:T=150410158' +
              '4:S=ALNI_Mae1yHotZvFo066PX75ZYAUGvQlVA;' +
              ' s_cc=true; s_sq=%5B%5BB%5D%5D',
    'DNT': '1'
}

param_list = {
    'DateFrom': {'type': 'Date'},
    'DateTo': {'type': 'Date'},
    'MeasureType': {'type': 'Enum', 'choices': [
        'Base', 'Advanced', 'Misc', 'Scoring',
        'Usage', 'Opponent', 'Defense']},
    'SeasonType': {'type': 'Enum', 'choices': [
        'Pre Season', 'Regular Season', 'Playoffs', 'All Star']},
    'PerMode': {'type': 'Enum', 'choices': [
        'PerGame', 'Per100Possessions', 'PerPossession',
        'Per100Plays', 'PerPlay', 'PerMinute', 'Per36',
        'Per40', 'Per48', 'Totals']},
    'PlayerOrTeam': {'type': 'Enum', 'choices': ['Player', 'Team', 'P', 'T']},
    'PtMeasureType': {'type': 'Enum', 'choices': [
        'Drives', 'Defense', 'CatchShoot', 'Passing', 'Possessions',
        'PullUpShot', 'Rebounding', 'Efficiency', 'SpeedDistance',
        'ElbowTouch', 'PostTouch', 'PaintTouch']}
}


def check_params(params):
    for key, value in params.items():
        if key in param_list:
            p = param_list[key]
            if p['type'] == 'Enum' and value not in p['choices']:
                suggestions = process.extract(value, p['choices'], limit=3)
                raise ValueError(
                    '{} is not a valid value for {}. Did you mean {}'.format(value, key, suggestions)
                )

            if p['type'] == 'Date' and value != '':
                parse(value)


def construct_full_url(base, params):
    s = base + '?'

    s += ''.join([
        '{}='.format(param) +
        str(value).replace(' ', '+') +
        '&' for param, value in params.items()])

    return s


def json_to_pandas(json, index):
    data = json['resultSets'][index]
    headers = data['headers']
    rows = data['rowSet']
    data_dict = [dict(zip(headers, row)) for row in rows]
    return pd.DataFrame(data_dict)


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
                suggestions = process.extract(
                    key,
                    self.default_params.keys(),
                    limit=3
                )
                raise ValueError(
                    '{} is not a valid value for {}. Did you mean: {}?'.format(value, key, suggestions)
                )

        return params

    def determine_file_path(self, params):
        param_string = ''
        for p in sorted(params):
            param_string += ',{}={}'.format(str(p), str(params[p]))
            # param_string += ',' + str(p) + '=' + str(params[p])
        param_hash = hashlib.sha1(param_string.encode('utf-8')).hexdigest()
        return data_dir + \
               self.base_url.split('/')[-1] + '/' + param_hash + '.csv'

    def get_data(self, passed_params=default_params, override_file=False):
        check_params(passed_params)
        params = self.set_params(passed_params)
        file_path = self.determine_file_path(params)

        if (not file_check(file_path)) or override_file:
            print(construct_full_url(self.base_url, params))
            r = requests.post(
                self.base_url,
                data=params,
                headers=request_headers
            )
            if r.status_code != 200:
                raise ConnectionError(
                    str(r.status_code) + ': ' + str(r.reason)
                )

            df = json_to_pandas(r.json(), self.index)
            df.to_csv(file_path)
            return df
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
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'StarterBench': '',
        'TeamID': '0',
        'VsConference': '',
        'VsDivision': '',
        'Weight': ''
    }


class PlayerPassDashboard(EndPoint):
    base_url = 'http://stats.nba.com/stats/playerdashptpass'
    default_params = {
        'DateFrom': '',
        'DateTo': '',
        'GameSegment': '',
        'LastNGames': '0',
        'LeagueID': '00',
        'Location': '',
        'Month': '0',
        'OpponentTeamID': '0',
        'Outcome': '',
        'PORound': '0',
        'PerMode': 'Totals',
        'Period': '0',
        'PlayerID': '',
        'Season': '2017-18',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'TeamID': '',
        'VsConference': '',
        'VsDivision': '',
    }
    index = 0


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


class PlayerAdvancedGameLogs(EndPoint):
    base_url = 'http://stats.nba.com/stats/playergamelogs'
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
        'PORound': '0',
        'PaceAdjust': 'N',
        'PerMode': 'Totals',
        'Period': '0',
        'PlusMinus': 'N',
        'Rank': 'N',
        'Season': '2017-18',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'ShotClockRange': '',
        'VsConference': '',
        'VsDivision': '',
    }


class TeamAdvancedGameLogs(EndPoint):
    base_url = 'http://stats.nba.com/stats/teamgamelogs'
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
        'PORound': '0',
        'PaceAdjust': 'N',
        'PerMode': 'Totals',
        'Period': '0',
        'PlusMinus': 'N',
        'Rank': 'N',
        'Season': '2017-18',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'ShotClockRange': '',
        'VsConference': '',
        'VsDivision': '',
    }


class ShotChartDetail(EndPoint):
    base_url = 'http://stats.nba.com/stats/shotchartdetail'
    default_params = {
        'AheadBehind': '',
        'CFID': '',
        'CFPARAMS': '',
        'ClutchTime': '',
        'Conference': '',
        'ContextFilter': '',
        'ContextMeasure': 'FGA',
        'DateFrom': '',
        'DateTo': '',
        'Division': '',
        'EndPeriod': '10',
        'EndRange': '28800',
        'GROUP_ID': '',
        'GameEventID': '',
        'GameID': '',
        'GameSegment': '',
        'GroupID': '',
        'GroupMode': '',
        'GroupQuantity': '5',
        'LastNGames': '0',
        'LeagueID': '00',
        'Location': '',
        'Month': '0',
        'OnOff': '',
        'OpponentTeamID': '0',
        'Outcome': '',
        'PORound': '0',
        'Period': '0',
        'PlayerID': '0',
        'PlayerID1': '',
        'PlayerID2': '',
        'PlayerID3': '',
        'PlayerID4': '',
        'PlayerID5': '',
        'PlayerPosition': '',
        'RangeType': '0',
        'RookieYear': '',
        'Season': '2017-18',
        'SeasonSegment': '',
        'SeasonType': 'Regular Season',
        'ShotClockRange': '',
        'StartPeriod': '1',
        'StartRange': '0',
        'StarterBench': '',
        'TeamID': '0',
        'VsConference': '',
        'VsDivision': '',
        'VsPlayerID1': '',
        'VsPlayerID2': '',
        'VsPlayerID3': '',
        'VsPlayerID4': '',
        'VsPlayerID5': '',
        'VsTeamID': ''
    }


class PlayByPlay(EndPoint):
    base_url = 'http://stats.nba.com/stats/playbyplayv2'
    default_params = {
        'EndPeriod': '10',
        'EndRange': '55800',
        'GameID': '0021700216',
        'RangeType': '2',
        'Season': '2017-18',
        'SeasonType': 'Regular Season',
        'StartPeriod': '1',
        'StartRange': '0'
    }

    def determine_file_path(self, params):
        return data_dir + 'playbyplayv2/' + params['Season'] \
               + '/' + params['GameID'] + '.csv'

    def update_data(self, season='2017-18', season_type='Regular Season'):
        log = TeamAdvancedGameLogs().get_data(
            {'Season': season, 'SeasonType': season_type},
            override_file=True
        )

        games = log.GAME_ID.unique()

        for g in games:
            if len(str(g)) < 10:
                g = '00' + str(g)

            self.get_data({
                'GameID': g, 'Season': season, 'SeasonType': season_type
            })


class BoxScoreEndPoint(EndPoint):
    default_params = {
        'EndPeriod': '10',
        'EndRange': '28800',
        'GameID': '',
        'RangeType': '0',
        'Season': '2017-18',
        'SeasonType': 'Regular Season',
        'StartPeriod': '1',
        'StartRange': '0'
    }

    def set_index(self, index):
        self.index = index

    def determine_file_path(self, params):
        box_score_type = self.base_url.split('https://stats.nba.com/stats/boxscore')[0].split('v2')[0]
        return data_dir + 'boxscore/' + params['GameID'] + '/' + box_score_type + '.csv'


class BoxScoreSummary(BoxScoreEndPoint):
    base_url = 'https://stats.nba.com/stats/boxscoresummaryv2'
    default_params = {
        'GameID': ''
    }
    index = 1


class BoxScoreTraditional(BoxScoreEndPoint):
    base_url = 'https://stats.nba.com/stats/boxscoretraditionalv2'


class BoxScoreAdvanced(BoxScoreEndPoint):
    base_url = 'https://stats.nba.com/stats/boxscoreadvancedv2'


class BoxScoreMisc(BoxScoreEndPoint):
    base_url = 'https://stats.nba.com/stats/boxscoremiscv2'


class BoxScoreScoring(BoxScoreEndPoint):
    base_url = 'https://stats.nba.com/stats/boxscorescoringv2'


class BoxScoreUsage(BoxScoreEndPoint):
    base_url = 'https://stats.nba.com/stats/boxscoreusagev2'


class BoxScoreFourFactors(BoxScoreEndPoint):
    base_url = 'https://stats.nba.com/stats/boxscorefourfactorsv2'


class BoxScoreTracking(BoxScoreEndPoint):
    base_url = 'https://stats.nba.com/stats/boxscoreplayertrackv2'


class BoxScoreHustle(EndPoint):
    base_url = 'https://stats.nba.com/stats/hustlestatsboxscore'
    default_params = {
        'GameID': ''
    }
    index = 1


class BoxScoreMatchups(EndPoint):
    base_url = 'http://stats.nba.com/stats/boxscorematchups'
    default_params = {
        'GameID': ''
    }

    def determine_file_path(self, params):
        return data_dir + 'boxscorematchups/' + params['GameID'] + '.csv'

    def update_data(self, season='2017-18', season_type='Regular Season'):
        log = TeamAdvancedGameLogs().get_data(
            {'Season': season, 'SeasonType': season_type},
            override_file=True
        )

        games = log.GAME_ID.unique()

        for g in games:
            if len(str(g)) < 10:
                g = '00' + str(g)
            self.get_data({'GameID': g})

    def aggregate_data(self, season='2017-18', season_type='Regular Season',
                       override_file=False):

        file_path = data_dir + '/boxscorematchups/aggregate_{}.csv'.format(season)

        if (not file_check(file_path)) or override_file:

            log = TeamAdvancedGameLogs().get_data({
                'Season': season, 'SeasonType': season_type},
                override_file=True
            )

            games = ['00' + str(g) if len(str(g)) < 10 else str(g)
                     for g in log.GAME_ID.unique()]

            season_df = pd.concat(
                [self.get_data({'GameID': g}) for g in games]
            )

            sum_col = [
                'AST', 'BLK', 'DEF_FOULS', 'FG3A', 'FG3M', 'FGA', 'FGM',
                'FTM', 'HELP_BLK', 'HELP_BLK_REC', 'OFF_FOULS', 'PLAYER_PTS',
                'POSS', 'SFL', 'TEAM_PTS', 'TOV'
            ]

            group_col = ['OFF_PLAYER_NAME', 'DEF_PLAYER_NAME']

            df = season_df.groupby(group_col)[sum_col].sum()
            df.reset_index(inplace=True)
            df = df[df['POSS'] >= 10]
            df.to_csv(file_path)
            return df
        else:
            return pd.read_csv(file_path)


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

    def get_data(self, passed_params=default_params, override_file=False):
        check_params(passed_params)
        params = self.set_params(passed_params)

        file_path = self.determine_file_path(params)

        if (not file_check(file_path)) or override_file:
            r = requests.post(
                self.base_url,
                data=params,
                headers=request_headers)

            print(str(r.status_code) + ': ' + construct_full_url(self.base_url, params))

            data = r.json()['resultSets'][1]

            headers = [
                'GROUP_SET_ON', 'TEAM_ID', 'TEAM_ABBREVIATION',
                'TEAM_NAME', 'VS_PLAYER_ID', 'VS_PLAYER_NAME',
                'COURT_STATUS_ON', 'GP_ON', 'MIN_ON', 'PLUS_MINUS_ON',
                'OFF_RATING_ON', 'DEF_RATING_ON', 'NET_RATING_ON'
            ]

            rows = data['rowSet']
            data_dict = [dict(zip(headers, row)) for row in rows]
            on_df = pd.DataFrame(data_dict)
            data = r.json()['resultSets'][2]

            headers = [
                'GROUP_SET_OFF', 'TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_NAME',
                'VS_PLAYER_ID', 'VS_PLAYER_NAME', 'COURT_STATUS_OFF',
                'GP_OFF', 'MIN_OFF', 'PLUS_MINUS_OFF', 'OFF_RATING_OFF',
                'DEF_RATING_OFF', 'NET_RATING_OFF']

            rows = data['rowSet']
            data_dict = [dict(zip(headers, row)) for row in rows]
            off_df = pd.DataFrame(data_dict)

            df = pd.merge(on_df, off_df,
                          on=['TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_NAME',
                              'VS_PLAYER_ID', 'VS_PLAYER_NAME']
                          )

            df.to_csv(file_path)

            return df

        else:
            print(file_path)
            return pd.read_csv(file_path)


class Standings(EndPoint):
    base_url = 'http://stats.nba.com/stats/leaguestandingsv3'
    default_params = {'LeagueID': '00',
                      'Season': '2017-18',
                      'SeasonType': 'Regular Season'}


class SynergyPlayerStats(EndPoint):
    base_url = 'https://stats-prod.nba.com/wp-json/statscms/v1/synergy/player/'
    default_params = {'category': 'Spotup',
                      'limit': '500',
                      'names': 'offensive',
                      'q': '2538084',
                      'season': '2017',
                      'seasonType': 'Reg'}

    synergy_request_headers = request_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        #'Cookie': 's_cc=true; s_fid=0C14240EE454CE98-1406F45DADF8283D; s_sq=%5B%5BB%5D%5D; s_vi=[CS]v1|2D626C7F05030B69-4000118620008578[CE]',
        'DNT': '1',
        'Host': 'stats-prod.nba.com',
        'Origin': 'https://stats.nba.com',
        'Referer': 'https://stats.nba.com/players/spot-up/?sort=Percentile&dir=-1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'
    }

    def get_data(self, passed_params=default_params, override_file=False):
        check_params(passed_params)
        params = self.set_params(passed_params)
        file_path = self.determine_file_path(params)

        if (not file_check(file_path)) or override_file:
            full_url = construct_full_url(self.base_url, params)
            r = requests.get(
                full_url,
                headers=self.synergy_request_headers
            )

            if r.status_code != 200:
                raise ConnectionError(
                    '{}:{}'.format(r.status_code, r.reason)
                )
            df = pd.DataFrame(r.json()['results'])
            df.to_csv(file_path)
            return df

        else:
            print(file_path)
            return pd.read_csv(file_path)


class DraftCombineAnthro(EndPoint):
    """
        Draft Combine Anthropology Data.
        Args:
            SeasonYear (str):
                Draft Season. Format: {start_year_long}-{end_year_short}

        Returns:
            Draft Combine Anthro (df): Draft Combine statistics from Season.
            Columns:
                FIRST_NAME
                HAND_LENGTH
                HAND_WIDTH
                HEIGHT_WO_SHOES
                HEIGHT_WO_SHOES_FT_IN
                HEIGHT_W_SHOES
                HEIGHT_W_SHOES_FT_IN
                LAST_NAME
                PLAYER_ID
                PLAYER_NAME
                POSITION
                STANDING_REACH
                STANDING_REACH_FT_IN
                TEMP_PLAYER_ID
                WEIGHT
                WINGSPAN
                WINGSPAN_FT_IN


    """

    base_url = 'https://stats.nba.com/stats/draftcombineplayeranthro'
    default_params = {
        'LeagueID': '00',
        'SeasonYear': '2017-18'
    }


class DraftCombineStrengthAgility(EndPoint):
    base_url = 'https://stats.nba.com/stats/draftcombinedrillresults'
    default_params = {
        'LeagueID': '00',
        'SeasonYear': '2017-18'
    }
