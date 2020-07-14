import io
import os

import chart_studio
import plotly.graph_objects as go
from PIL import Image as PILImage
from chart_studio.plotly import image as PlotlyImage
from plotly.offline import plot
from plotly.subplots import make_subplots

# configure chart studio
chart_studio.tools.set_credentials_file(username=os.environ['CHART_STUDIO_USERNAME'],
                                        api_key=os.environ['CHART_STUDIO_APIKEY'])


def plot_multiple_bar_chart(indices, counts, title, subtitles):
    fig = make_subplots(rows=len(counts), cols=len(counts[0]), shared_yaxes=True)
    i = 1
    for index_row, count_row, subtitle_row in zip(indices, counts, subtitles):
        j = 1
        for index_col, count_col, subtitle_col in zip(index_row, count_row, subtitle_row):
            fig.append_trace(go.Bar(name=subtitle_col, x=index_col, y=count_col), row=i, col=j)
            j += 1

        i += 1
    # fig.update_xaxes(tickfont=dict(size=8))
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

    img_bytes = PlotlyImage.get(fig, width=800, height=1500)
    image = PILImage.open(io.BytesIO(img_bytes))

    return div, image
