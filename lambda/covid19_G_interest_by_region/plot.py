import plotly.express as px
from plotly.offline import plot


def plot_geograph(df, key, title):
    df = df[df[key] != 0]
    fig = px.scatter_geo(df,
                         lat = "Latitude (average)",
                         lon = "Longitude (average)",
                         # locations="Alpha-3 code",
                         # locationmode="ISO-3",
                         color="country",  # which column to use to set the color of markers
                         hover_name=key,  # column added to hover information
                         size=key,  # size of markers
                         projection="natural earth",
                         title=title)
    div = plot(fig, output_type='div', auto_open=False, image_filename='plot_img')

    return div
