import pandas as pd
import plotly.graph_objects as go

# Load and process the data
df = pd.read_csv('bb_tokens_table.csv')

# Exclude the 'Total' column
df_filtered = df.iloc[:, :-1]

z = df_filtered.iloc[:, 1:].values.T

fig = go.Figure(data=[go.Surface(
    z=z,
    x=df_filtered['Date'],
    y=df_filtered.columns[1:],
    colorscale='Viridis',
)])

z_avg = z.mean()

fig.update_layout(
    scene = dict(
        xaxis_title='',
        yaxis_title='',
        zaxis_title='Token Count',
        xaxis = dict(
            tickformat='%Y',
            dtick='M12', 
            range=[df_filtered['Date'].min(), df_filtered['Date'].max()],
            tickmode='linear' 
        ),
        yaxis = dict(
            tickvals=list(range(len(df_filtered.columns[1:]))),
            ticktext=df_filtered.columns[1:]
        ),
        zaxis = dict(
            range=[z.min(), z.max()]
        )
    ),
    autosize=True,
    margin=dict(l=0, r=0, b=0, t=0)
)

# Update the Surface trace instead of Scatter3d
fig.update_traces(selector=dict(type='surface'), surfacecolor=z, cmin=z.min(), cmax=z.max())

fig.show()
fig.write_html("bb_tokens_3d_surface.html")