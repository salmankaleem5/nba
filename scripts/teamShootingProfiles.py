from util.data import TeamShootingStats, GeneralTeamStats
from util.reddit import print_reddit_table
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go

tss = TeamShootingStats()
gts = GeneralTeamStats()

season = '2017-18'
range_type = 'By Zone'
per_mode = 'Per100Possessions'
data_override = False

full_year_shots_df = tss.get_data({'Season': '2016-17', 'DistanceRange': range_type, 'MeasureType': 'Base'},
                                  override_file=data_override)
full_year_general_df = gts.get_data({'Season': '2016-17', 'PerMode': 'Totals', 'MeasureType': 'Base'},
                                    override_file=data_override)
offensive_shots_df = tss.get_data({'Season': season, 'DistanceRange': range_type, 'MeasureType': 'Base'},
                                  override_file=data_override)
defensive_shots_df = tss.get_data({'Season': season, 'DistanceRange': range_type, 'MeasureType': 'Opponent'},
                                  override_file=data_override)
offensive_general_df = gts.get_data({'Season': season, 'PerMode': per_mode, 'MeasureType': 'Base'},
                                    override_file=data_override)
defensive_general_df = gts.get_data({'Season': season, 'PerMode': per_mode, 'MeasureType': 'Opponent'},
                                    override_file=data_override)
advanced_df = gts.get_data({'Season': season, 'PerMode': per_mode, 'MeasureType': 'Advanced'},
                           override_file=data_override)

zones = tss.get_zones(range_type)
averages = {}

for z in zones:
    fg_pct = full_year_shots_df[z + '_FGM'].sum() / full_year_shots_df[z + '_FGA'].sum()
    if '3' in z:
        averages[z] = fg_pct * 3
    else:
        averages[z] = fg_pct * 2

averages['Free Throw'] = full_year_general_df['FTM'].sum() / full_year_general_df['FTA'].sum()

teams = offensive_shots_df.TEAM_NAME.unique()
offensive_profiles = []
defensive_profiles = []

for t in teams:
    team_offensive_shots_df = offensive_shots_df[offensive_shots_df.TEAM_NAME == t]
    team_defensive_shots_df = defensive_shots_df[defensive_shots_df.TEAM_NAME == t]

    offensive_profile = {
        'Team': t,
        'Total Rating': 0,
        'FT Rate': offensive_general_df[offensive_general_df.TEAM_NAME == t].FTA.iloc[0],
        'True Shooting': (offensive_general_df[offensive_general_df.TEAM_NAME == t].PTS.iloc[0] / (
            offensive_general_df[offensive_general_df.TEAM_NAME == t].FGA.iloc[0] + (
                0.44 * offensive_general_df[offensive_general_df.TEAM_NAME == t].FTA.iloc[0]))) * 100
    }

    offensive_profile['FGA Rate'] = 100 - (offensive_profile['FT Rate'] * 0.44)

    defensive_profile = {
        'Team': t,
        'Total Rating': 0,
        'FT Rate': defensive_general_df[defensive_general_df.TEAM_NAME == t].OPP_FTA.iloc[0],
        'True Shooting': (defensive_general_df[defensive_general_df.TEAM_NAME == t].OPP_PTS.iloc[0] / (
            defensive_general_df[defensive_general_df.TEAM_NAME == t].OPP_FGA.iloc[0] + (
                0.44 * defensive_general_df[offensive_general_df.TEAM_NAME == t].OPP_FTA.iloc[0]))) * 100
    }

    defensive_profile['FGA Rate'] = 100 - (defensive_profile['FT Rate'] * 0.44)

    offense_total_fga = 0
    defense_total_fga = 0

    for z in zones:
        offense_total_fga += team_offensive_shots_df[z + '_FGA'].iloc[0]
        defense_total_fga += team_defensive_shots_df[z + '_FGA'].iloc[0]

    for z in zones:
        offensive_profile[z + ' Rate'] = (team_offensive_shots_df[z + '_FGA'].iloc[0] / offense_total_fga) * \
                                         offensive_profile['FGA Rate']
        defensive_profile[z + ' Rate'] = (team_defensive_shots_df[z + '_FGA'].iloc[0] / defense_total_fga) * \
                                         defensive_profile['FGA Rate']

        offensive_profile['Total Rating'] += offensive_profile[z + ' Rate'] * averages[z]
        defensive_profile['Total Rating'] += defensive_profile[z + ' Rate'] * averages[z]

    offensive_profile['Total Rating'] += offensive_profile['FT Rate'] * averages['Free Throw']
    defensive_profile['Total Rating'] += defensive_profile['FT Rate'] * averages['Free Throw']

    offensive_profile['Diff'] = offensive_profile['Total Rating'] - (offensive_profile['True Shooting'])
    defensive_profile['Diff'] = defensive_profile['Total Rating'] - (defensive_profile['True Shooting'])

    offensive_profiles.append(offensive_profile)
    defensive_profiles.append(defensive_profile)

offensive_profile_df = pd.DataFrame(offensive_profiles).sort_values(by='Team', ascending=True)
defensive_profile_df = pd.DataFrame(defensive_profiles).sort_values(by='Team', ascending=True)

offensive_profile_df['Corner 3 Rate'] = offensive_profile_df['Left Corner 3 Rate'] + offensive_profile_df[
    'Right Corner 3 Rate']
defensive_profile_df['Corner 3 Rate'] = defensive_profile_df['Left Corner 3 Rate'] + defensive_profile_df[
    'Right Corner 3 Rate']
offensive_profile_df['FT Rate'] = offensive_profile_df['FT Rate'] * 0.44
defensive_profile_df['FT Rate'] = defensive_profile_df['FT Rate'] * 0.44

print(averages)
columns_to_print = ['Team', 'Total Rating', 'True Shooting', 'Restricted Area Rate', 'In The Paint (Non-RA) Rate',
                    'Mid-Range Rate', 'Corner 3 Rate', 'Above the Break 3 Rate', 'FT Rate']
print_reddit_table(offensive_profile_df, columns_to_print)
print_reddit_table(defensive_profile_df, columns_to_print)

# offensive_trace = go.Scatter(
#     x=offensive_profile_df['Total Rating'],
#     y=offensive_profile_df['True Shooting'],
#     text=offensive_profile_df['Team'],
#     mode='markers',
#     marker=dict(
#         size=20
#     ),
#     textposition='top center'
# )
#
# defensive_trace = go.Scatter(
#     x=defensive_profile_df['Total Rating'],
#     y=defensive_profile_df['True Shooting'],
#     text=defensive_profile_df['Team'],
#     mode='markers',
#     marker=dict(
#         size=20
#     ),
#     textposition='top center'
# )
#
# offensive_layout = go.Layout(
#     title='Offensive Shot Profiles',
#     xaxis=dict(
#         title='Shot Rating'
#     ),
#     yaxis=dict(
#         title='Actual Points Per Shot'
#     ),
#     showlegend=False
# )
#
# defensive_layout = go.Layout(
#     title='Defensive Shot Profiles',
#     xaxis=dict(
#         title='Shot Rating'
#     ),
#     yaxis=dict(
#         title='Actual Points Per Shot'
#     ),
#     showlegend=False
# )
#
# offensive_fig = go.Figure(data=[offensive_trace], layout=offensive_layout)
# py.plot(offensive_fig, filename='Offensive Shot Profiles')
#
# defensive_fig = go.Figure(data=[defensive_trace], layout=defensive_layout)
# py.plot(defensive_fig, filename='Defensive Shot Profiles')
#
#
# total_trace = go.Scatter(
#     x=offensive_profile_df['Diff'],
#     y=defensive_profile_df['Diff'],
#     text=offensive_profile_df['Team'],
#     mode='markers',
#     marker=dict(
#         size=20
#     ),
#     textposition='top center'
# )
#
# total_layout = go.Layout(
#     title='Total Difference',
#     xaxis=dict(
#         title='Offensive Difference'
#     ),
#     yaxis=dict(
#         title='Defensive Difference'
#     ),
#     showlegend=False
# )
#
# total_fig = go.Figure(data=[total_trace], layout=total_layout)
# py.plot(total_fig, filename='Total Shot Profile Diff')
