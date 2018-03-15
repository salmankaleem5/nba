from util.data import data_dir, file_check
import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_season_schedule(season='2017-18', override_file=False):
    file_path = data_dir + season + '_schedule.csv'

    if (not file_check(file_path)) or override_file:

        base_url = 'https://www.basketball-reference.com/leagues/NBA_2018_games-{}.html'
        months = ['october', 'november', 'december', 'january', 'february', 'march', 'april']

        schedule_data = []
        for month in months:
            r = requests.post(base_url.format(month))
            html = r.content
            soup = BeautifulSoup(html)
            if month == months[0]:
                headers = [th.getText() for th in soup.find_all('tr')[0].find_all('th')]
            rows = soup.find_all('tr')[1:]
            schedule_data.extend([[td.getText() for td in rows[i].find_all(['th', 'td'])] for i in range(len(rows))])

        schedule_df = pd.DataFrame(schedule_data, columns=headers)
        schedule_df.fillna(0)

        schedule_df.rename(columns={
            'Home/Neutral': 'Home',
            'Visitor/Neutral': 'Visitor'
                            }, inplace=True)
        schedule_df.to_csv(file_path)
        return schedule_df
    else:
        return pd.read_csv(file_path)
