from util.espn import get_rpm

import plotly.plotly as py
import plotly.graph_objs as go

df = get_rpm()

df = df[df['MPG'] >= 10]
df = df[df['GP'] >= 50]

positions = df['POS'].unique()

for p in positions:
    traces = []
    pos_df = df[df.POS == p]

    trace_df = pos_df
    traces.append(go.Scatter(
        x=trace_df.DRPM,
        y=trace_df.ORPM,
        text=trace_df.NAME,
        mode='markers',
        marker=dict(
            size=14,
            color='rgb(0, 0, 0)',
            opacity=0.3
        )
    ))

    trace_df = pos_df.sort_values(by='ORPM', ascending=True).head(5)
    traces.append(go.Scatter(
        x=trace_df.DRPM,
        y=trace_df.ORPM,
        text=trace_df.NAME,
        mode='markers+text',
        marker=dict(
            size=14,
            color=trace_df.RPM,
            colorscale=' Bluered',
            opacity=1
        ),
        textposition='top center'
    ))

    trace_df = pos_df.sort_values(by='ORPM', ascending=False).head(5)
    traces.append(go.Scatter(
        x=trace_df.DRPM,
        y=trace_df.ORPM,
        text=trace_df.NAME,
        mode='markers+text',
        marker=dict(
            size=14,
            color=trace_df.RPM,
            colorscale=' Bluered',
            opacity=1
        ),
        textposition='top center'
    ))

    trace_df = pos_df.sort_values(by='DRPM', ascending=True).head(5)
    traces.append(go.Scatter(
        x=trace_df.DRPM,
        y=trace_df.ORPM,
        text=trace_df.NAME,
        mode='markers+text',
        marker=dict(
            size=14,
            color=trace_df.RPM,
            colorscale=' Bluered',
            opacity=1
        ),
        textposition='top center'
    ))

    trace_df = pos_df.sort_values(by='DRPM', ascending=False).head(5)
    traces.append(go.Scatter(
        x=trace_df.DRPM,
        y=trace_df.ORPM,
        text=trace_df.NAME,
        mode='markers+text',
        marker=dict(
            size=14,
            color=trace_df.RPM,
            colorscale=' Bluered',
            opacity=1
        ),
        textposition='top center'
    ))

    layout = dict(
        title=p + ' RPM',
        showlegend=False,
        xaxis=dict(
            title='DRPM',
            showgrid=False,
            zerolinecolor='rgb(209, 209, 209)'
        ),
        yaxis=dict(
            title='ORPM',
            showgrid=False,
            zerolinecolor='rgb(209, 209, 209)'
        )
    )

    fig = dict(
        data=traces,
        layout=layout
    )
    py.plot(fig, filename=p + ' RPM')
