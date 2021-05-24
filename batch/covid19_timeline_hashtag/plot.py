import plotly.graph_objects as go
from plotly.offline import plot

def plot_bar_chart(index, counts, title):
    """
    plot bar chart
    :param index: x - axis, usually the index
    :param counts: y - axis, usually counts
    :param title:
    :return:
    """

    trace = go.Bar(x=index, y=counts)
    layout = go.Layout(
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

    fig = go.Figure(data=[trace], layout=layout)
    div = plot(fig, output_type='div', auto_open=False, image_filename='plot_img')

    return div
