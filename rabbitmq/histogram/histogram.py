import pandas as pd
import plotly.graph_objs as go
import writeToS3 as s3
from plotly.offline import plot


def plot_freq(index, counts, interval, localPath, remotePath):
    if interval == '1T':
        freq = '1 Minute'
    elif interval == '1H':
        freq = '1 Hour'
    elif interval == '6H':
        freq = '6 Hours'
    elif interval == '1D':
        freq = '1 Day'
    elif interval == '1W':
        freq = '1 Week'
    elif interval == '1M':
        freq = '1 Month'
    elif interval == '1Q':
        freq = '1 Quarter'
    elif interval == '6M':
        freq = '6 Months'
    elif interval == '1A':
        freq = '1 Year'
    else:
        freq = 'Undefined'
    
    trace = go.Bar(x=index,y=counts,marker=dict(color='rgba(200,75,73,1.0)',
            line=dict(color='rgba(111,11,9,1.0)',width=2)))
    layout = dict(
            title='count of posts over time (interval = ' + freq + ')',
            font=dict(family='Arial',size=12),
            yaxis=dict(
                showgrid=True,
                showline=True,
                showticklabels=True,
                linecolor='rgba(102, 102, 102, 0.8)',
                linewidth=2
            ),
            xaxis1=dict(
                #autotick=False,
                type='date',
                tickformat='%x %X',
                zeroline=True,
                showline=True,
                showticklabels=True,
                showgrid=True
            ),
            margin=dict(
                l=70,
                r=70,
                t=70,
                b=70,
            )
        )
        
    fig = go.Figure(data=[trace], layout=layout)
    div = plot(fig, output_type='div',image='png',auto_open=False, image_filename='plot_img')

    fname_div = 'div.html'
    with open(localPath + fname_div,"w") as f:
        f.write(div)
    s3.upload(localPath, remotePath,fname_div)
    div_url = s3.generate_downloads(remotePath,fname_div)

    return div_url


def count_freq(df, time_col_name, time_freq, time_unit):
    # convert time column to datetime
    df[time_col_name] = pd.to_datetime(df[time_col_name],unit=time_unit)
    # set index to datetime
    df.set_index(df[time_col_name],inplace=True)

    return df[time_col_name].resample(time_freq).count()

        
    
