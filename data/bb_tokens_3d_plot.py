import pandas as pd
import plotly.graph_objects as go

# Load and process the data
df = pd.read_csv('bb_tokens_table.csv')
z = df.iloc[:, 1:].values.T

fig = go.Figure(data=[go.Surface(
    z=z,
    x=df['Date'],
    y=df.columns[1:],
    colorscale='Viridis',
)])

# Update the layout
fig.update_layout(
    title='Beige Book Token Counts Over Time by District (1970-2023)',
    scene = dict(
        xaxis_title='Date',
        yaxis_title='District',
        zaxis_title='Token Count',
        xaxis = dict(
            tickformat='%Y',
            dtick='M60',
            range=[df['Date'].min(), df['Date'].max()]
        )
    ),
    autosize=False,
    width=1200,
    height=800,
    margin=dict(l=65, r=50, b=65, t=90)
)


fig.update_traces(surfacecolor=z, cmin=z.min(), cmax=z.max())

fig.show()
fig.write_html("bb_tokens_3d_surface.html")