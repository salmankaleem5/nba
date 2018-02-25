from util.nba_stats import GeneralPlayerStats
import pandas as pd
import numpy as np


def determine_from_listed_position():
    general_stats_ep = GeneralPlayerStats()

    guards = general_stats_ep.get_data({'Season': '2017-18', 'PlayerPosition': 'G'})
    forwards = general_stats_ep.get_data({'Season': '2017-18', 'PlayerPosition': 'F'})
    centers = general_stats_ep.get_data({'Season': '2017-18', 'PlayerPosition': 'C'})

    guards['G'] = 1
    forwards['F'] = 1
    centers['C'] = 1

    merge_df = pd.merge(guards, forwards, on=['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'TEAM_ID'], how='outer')
    merge_df = pd.merge(merge_df, centers, on=['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'TEAM_ID'], how='outer')

    merge_df = merge_df[['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'TEAM_ID', 'G', 'F', 'C']]
    merge_df = merge_df.fillna(0)

    conditions = [
        ((merge_df['G'] == 1) & (merge_df['F'] == 0) & (merge_df['C'] == 0)),
        ((merge_df['F'] == 1) & (merge_df['C'] == 0)),
        (merge_df['C'] == 1)
    ]
    choices = ['Guard', 'Wing', 'Big']

    merge_df['POSITION'] = np.select(conditions, choices, default='None')
    return merge_df


def determine_from_tracking_data():


determine_from_listed_position()