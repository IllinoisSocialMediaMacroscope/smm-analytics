import io
import os

import chart_studio
import plotly.express as px
from PIL import Image as PILImage
from chart_studio.plotly import image as PlotlyImage
from plotly.offline import plot

# configure chart studio
chart_studio.tools.set_credentials_file(username=os.environ['CHART_STUDIO_USERNAME'],
                                        api_key=os.environ['CHART_STUDIO_APIKEY'])


def plot_geograph(df, key, title):
    df = df[df[key] != 0]
    fig = px.scatter_mapbox(df,
                            lat="Latitude (average)",
                            lon="Longitude (average)",
                            # locations="Alpha-3 code",
                            # locationmode="ISO-3",
                            color="country",  # which column to use to set the color of markers
                            hover_name=key,  # column added to hover information
                            size=key,  # size of markers
                            zoom=1,
                            title=title)
    fig.update_layout(mapbox_style="open-street-map", height=600)
    div = plot(fig, output_type='div', auto_open=False, image_filename='plot_img')

    img_bytes = PlotlyImage.get(fig)
    image = PILImage.open(io.BytesIO(img_bytes))

    return div, image
