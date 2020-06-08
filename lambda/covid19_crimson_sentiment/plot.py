import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot


def plot_multiple_pie_chart(labels, values, title):
    fig = make_subplots(rows=len(values), cols=len(values[0]),
                        specs=[[{"type": "pie"} for j in range(len(values[0]))] for i in range(len(values))])

    i = 1
    for label, value in zip(labels, values):
        j = 1
        for label_col, value_col in zip(label, value):
            fig.add_trace(go.Pie(labels=label_col, values=value_col,
                                 hoverinfo='label+percent+value',
                                 textinfo='label'), row=i, col=j)
            i += 1

    fig.update_layout(
        title_text= title,
        font=dict(family='Arial', size=12),
        margin=dict(
            l=70,
            r=70,
            t=70,
            b=70,
        ))
    div = plot(fig, output_type='div', auto_open=False, image_filename='plot_img')

    return div
