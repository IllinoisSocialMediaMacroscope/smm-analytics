import random

import numpy as np
import plotly as py
import plotly.graph_objects as go
from plotly.offline import plot

import chart_studio
from PIL import Image as PILImage
from chart_studio.plotly import image as PlotlyImage
import os
import io

# configure chart studio
chart_studio.tools.set_credentials_file(username=os.environ['CHART_STUDIO_USERNAME'],
                                        api_key=os.environ['CHART_STUDIO_APIKEY'])

def word_cloud(words, scores):
    lower, upper = 10, 80
    frequency = [round((((x - min(scores)) / (max(scores) - min(scores))) ** 1.5) * (
            upper - lower) + lower) for x in scores]
    colors = [py.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for
              i in range(len(scores))]

    # set location
    x = list(np.arange(0, len(scores), 0.5))
    y = [i for i in range(len(scores))]
    random.shuffle(x)
    random.shuffle(y)

    data = go.Scatter(
        x=x,
        y=y,
        mode='text',
        text=words,
        hovertext=['{0} {1}'.format(w, s, format(s, '.2%')) for w, s in
                   zip(words, scores)],
        hoverinfo='text',
        textfont={
            'size': frequency,
            'color': colors,
            'family': 'Arial'

        }
    )

    layout = go.Layout(
        {
            'xaxis':
                {
                    'showgrid': False,
                    'showticklabels': False,
                    'zeroline': False,
                },
            'yaxis':
                {
                    'showgrid': False,
                    'showticklabels': False,
                    'zeroline': False,
                },
            'margin':
                {
                    't':10,
                    'b':10,
                    'l':10,
                    'r':10
                }
        })

    fig = go.Figure(data=[data], layout=layout)

    # save the plot
    div = plot(fig, output_type="div", auto_open=False, image_filename="word_cloud_img")

    img_bytes = PlotlyImage.get(fig)
    image = PILImage.open(io.BytesIO(img_bytes))

    return div, image
