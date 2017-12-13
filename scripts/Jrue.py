import plotly.plotly as py
import plotly.graph_objs as go

trace1 = go.Bar(
    x=['Transition', 'Isolation', 'Pick and Roll', 'Spot Up', 'Cut', 'Off Screen'],
    y=[11.5, 7.5, 50.7, 11.4, 2.2, 2.5],
    name='2016-17',
    marker=dict(color='rgb(0,43,92)')
)

trace2 = go.Bar(
    x=['Transition', 'Isolation', 'Pick and Roll', 'Spot Up', 'Cut', 'Off Screen'],
    y=[17.5, 11.1, 20.9, 20.6, 5.9, 9.5],
    name='2017-18',
    marker=dict(color='rgb(227,24,55)')
)

data = [trace1, trace2]
layout = go.Layout(
    barmode='group'
)

fig = go.Figure(data=data, layout=layout)
py.plot(fig, filename='Jrue Play Types')
