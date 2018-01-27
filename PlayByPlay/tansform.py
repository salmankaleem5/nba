from util.util import merge_shot_pbp_for_game


def determine_home_visitor(pbp_df):
    col = 'PLAYER1_TEAM_ABBREVIATION'
    teams = pbp_df[col].unique()[1:]
    home_df = pbp_df[pbp_df['VISITORDESCRIPTION'].isnull()]
    if len(home_df[home_df[col] == teams[0]]) > len(home_df[home_df[col] -- teams[1]]):
        return teams[0], teams[1]
    else:
        return teams[1], teams[0]


def get_initial_lineup(pbp_df, team, period):
    pbp_df = pbp_df[pbp_df['PLAYER1_TEAM_ABBREVIATION'] == team]
    pbp_df = pbp_df[pbp_df['PERIOD'] == period]
    subs_df = pbp_df[pbp_df.EVENTMSGTYPE == 8]
    players = []
    subbed_in = []
    for ix, sub in subs_df.iterrows():
        player_in = sub.PLAYER2_NAME
        player_out = sub.PLAYER1_NAME
        if player_out not in subbed_in:
            players.append(player_out)
        subbed_in.append(player_in)
        if len(players) == 5:
            return players

    others = pbp_df.PLAYER1_NAME.unique()
    others = [str(i) for i in others]

    others = list(filter(lambda x: x != 'nan', others))
    others = list(filter(lambda x: x != 'None', others))
    others = list(filter(lambda x: x not in subbed_in, others))

    for p in others:
        if p not in players:
            players.append(p)
            if len(players) == 5:
                return players

    raise ValueError('Not enough players')


def transform_game(game_id, season, season_type='Regular Season'):
    pbp_df = merge_shot_pbp_for_game(season, game_id, season_type)
    home_team, visitor_team = determine_home_visitor(pbp_df)

    home_players = []
    visitor_players = []

    data = []

    for ix, e in pbp_df.iterrows():
        # Event is the start of the quarter
        if e.EVENTMSGTYPE == 12:
            home_players = get_initial_lineup(pbp_df, home_team, e.PERIOD)
            visitor_players = get_initial_lineup(pbp_df, visitor_team, e.PERIOD)
            continue

        if e.EVENTMSGTYPE == 8:


transform_game('0021700001', '2017-18')