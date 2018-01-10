from bs4 import BeautifulSoup
import pandas as pd
import requests

from util.nba_stats import data_dir

import plotly.plotly as py
import plotly.graph_objs as go


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
df.RPM = df.RPM.astype(float)

df.to_csv(data_dir + 'RPM.csv')

traces = []
for t in df.TEAM.unique():
    team_df = df[df.TEAM == t]
    traces.append(go.Scatter(
        x=team_df.TEAM,
        y=team_df.RPM,
        text=team_df.NAME,
        mode='markers'
    ))

traces.sort(key=lambda x: -x.y.mean())
py.plot(traces, filename='RPM')
