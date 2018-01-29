from util.nba_stats import PlayByPlay


pbp_ep = PlayByPlay()


def determine_home_and_visitor(pbp_df):
    teams = pbp_df[pbp_df['PLAYER1_TEAM_ABBREVIATION']]['PLAYER1_TEAM_ABBREVIATION'].unique()
    return teams


def transform_pbp_for_game(game_id, season, season_type='Regular Season'):
    pbp_df = pbp_ep.get_data({'GameID': game_id, 'Season': season, 'SeasonType': season_type}, override_file=True)

    teams = {}
    teams['home'], teams['visitor'] = determine_home_and_visitor(pbp_df)


transform_pbp_for_game('0027100002', '2017-18')
