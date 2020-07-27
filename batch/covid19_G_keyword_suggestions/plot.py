import plotly.graph_objects as go
from plotly.offline import plot


def plot_table(title, header: list, cell: list):
    fig = go.Figure(data=[go.Table(header=dict(values=header), cells=dict(values=cell))])
    fig.update_layout(
        title_text=title,
        font=dict(family='Arial', size=12),
        autosize=True,
        margin=dict(
            l=70,
            r=70,
            t=70,
            b=70,
        )
    )
    div = plot(fig, output_type='div', auto_open=False, image_filename='plot_img')

    return div
