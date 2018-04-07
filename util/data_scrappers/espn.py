from util.data import data_dir, file_check
import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_rpm():
    file_path = data_dir + 'RPM/' + str(datetime.date.today()) + '.csv'

    if not file_check(file_path):
        rpm_url = 'http://www.espn.com/nba/statistics/rpm/_/page/{page}/sort/RPM'
        headers = []
        data = []
        for p in range(1, 12):
            r = requests.post(rpm_url.format(page=p))
            html = r.content
            soup = BeautifulSoup(html)
            if p == 1:
                headers = [th.getText() for th in soup.find_all('tr')[0].find_all('td')]
            rows = soup.find_all('tr')[1:]
            data.extend([[td.getText() for td in rows[i].find_all('td')] for i in range(len(rows))])

        df = pd.DataFrame(data, columns=headers)
        df.NAME = df.NAME.apply(lambda x: x.split(',')[0])
        df.to_csv(file_path)
        return df
    else:
        return pd.read_csv(file_path)