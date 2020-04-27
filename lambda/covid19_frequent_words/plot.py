from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def plot_multiple_bar_chart(indices, counts, title, subtitles):
    fig = make_subplots(rows=1, cols=3)

    i = 1
    for index, count, subtitle in zip(indices, counts, subtitles):
        fig.append_trace(go.Bar(name=subtitle, x=index, y=count), row=1, col=i)
        i += 1

    fig.update_layout(
        title_text=title,
        font=dict(family='Arial', size=12),
        margin=dict(
            l=70,
            r=70,
            t=70,
            b=70,
        ))
    div = plot(fig, output_type='div', image='png', auto_open=False, image_filename='plot_img')

    return div
