from plotly.graph_objs import *
from plotly.offline import plot
import chart_studio
from PIL import Image as PILImage
from chart_studio.plotly import image as PlotlyImage
import os
import io


# configure chart studio
chart_studio.tools.set_credentials_file(username=os.environ['CHART_STUDIO_USERNAME'],
                                        api_key=os.environ['CHART_STUDIO_APIKEY'])


def plot_bar_chart(index, counts, title):
    """
    plot bar chart
    :param index: x - axis, usually the index
    :param counts: y - axis, usually counts
    :param title:
    :return:
    """

    trace = Bar(x=index, y=counts,
                marker=dict(color='rgba(200,75,73,1.0)',
                            line=dict(color='rgba(111,11,9,1.0)',width=2)))
    layout = Layout(
        title=title,
        font=dict(family='Arial', size=12),
        yaxis=dict(
            showgrid=True,
            showline=True,
            showticklabels=True,
            linecolor='rgba(102, 102, 102, 0.8)',
            linewidth=2
        ),
        margin=dict(
            l=70,
            r=70,
            t=70,
            b=70,
        )
    )

    fig = Figure(data=[trace], layout=layout)
    div = plot(fig, output_type='div', image='png', auto_open=False, image_filename='plot_img')

    img_bytes = PlotlyImage.get(fig)
    image = PILImage.open(io.BytesIO(img_bytes))

    return div, image
