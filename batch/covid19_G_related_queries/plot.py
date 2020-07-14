import io

import plotly.graph_objects as go
from plotly.offline import plot
from plotly.subplots import make_subplots


def plot_multiple_bar_chart(indices, counts, title, subtitles):
    fig = make_subplots(rows=len(counts), cols=len(counts[0]))  # , shared_yaxes=True)
    i = 1
    for index_row, count_row, subtitle_row in zip(indices, counts, subtitles):
        j = 1
        for index_col, count_col, subtitle_col in zip(index_row, count_row, subtitle_row):
            fig.append_trace(go.Bar(name=subtitle_col, x=index_col, y=count_col), row=i, col=j)
            j += 1

        i += 1

    fig.update_layout(
        title_text=title,
        font=dict(family='Arial', size=12),
        autosize=True,
        margin=dict(
            l=70,
            r=70,
            t=70,
            b=70,
        ),
        height=1500
    )
    div = plot(fig, output_type='div', auto_open=False, image_filename='plot_img')

    return div
