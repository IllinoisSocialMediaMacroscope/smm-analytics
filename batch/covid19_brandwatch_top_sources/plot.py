import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot

import chart_studio
from PIL import Image as PILImage
from chart_studio.plotly import image as PlotlyImage
import os
import io

# configure chart studio
chart_studio.tools.set_credentials_file(username=os.environ['CHART_STUDIO_USERNAME'],
                                        api_key=os.environ['CHART_STUDIO_APIKEY'])

def plot_multiple_pie_chart(labels, values, subtitles):
    fig = make_subplots(rows=1, cols=2, subplot_titles=subtitles,
                        specs=[[{"type": "pie"}, {"type": "pie"}]])

    i = 1
    for label, value, subtitle in zip(labels, values, subtitles):
        fig.add_trace(go.Pie(name=subtitle, labels=label, values=value,
                             hoverinfo='label+percent+value',
                             textinfo='label'), row=1, col=i)
        i += 1

    fig.update_layout(
        font=dict(family='Arial', size=12),
        margin=dict(
            l=70,
            r=70,
            t=70,
            b=70,
        ))
    div = plot(fig, output_type='div', auto_open=False, image_filename='plot_img')

    img_bytes = PlotlyImage.get(fig)
    image = PILImage.open(io.BytesIO(img_bytes))

    return div, image
