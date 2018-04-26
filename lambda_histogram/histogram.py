import csv
import os
import pandas as pd
import plotly.graph_objs as go
from plotly import tools
from plotly.offline import plot
import writeToS3 as s3

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


def count_freq(df, time_col_name, content_col_name, time_freq ,time_unit):
    # convert time column to datetime
    df[time_col_name] = pd.to_datetime(df[time_col_name],unit=time_unit)
    # set index to datetime
    df.set_index(df[time_col_name],inplace=True)

    return df[content_col_name].resample(time_freq).count()



def lambda_handler(event, context):    
    # download the social media data to local lambda /tmp
    localPath = '/tmp/' + event['s3FolderName'] + '/'
    filename = event['filename']
    remotePath = event['remoteReadPath']

    if not os.path.exists(localPath):
        os.makedirs(localPath)
    
    s3.downloadToDisk(filename=filename,localpath=localPath, remotepath=remotePath)

    # read it into csv
    Array = []
    try:
        with open(localPath + filename,'r',encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                for row in reader:
                    Array.append(row)
            except Exception as e:
                pass
    except:
        with open(localReadPath + filename,'r',encoding="ISO-8859-1") as f:
            reader = csv.reader(f)
            try:
                for row in reader:
                    Array.append(row)
            except Exception as e:
                pass

    df = pd.DataFrame(Array[1:],columns=Array[0])
    print(df.columns)
    # tweet
    if 'created_at' in df.columns:
        # default at 1 hour
        if 'interval' in event:
            interval = event['interval']
        else:
            interval = '1H'
        freq = count_freq(df, 'created_at', 'created_at', interval, 'ns')

    # twitter user
    elif 'author_created_at' in df.columns:
        # default at 1M
        if 'interval' in event:
            interval = event['interval']
        else:
            interval = '1M'
        freq = count_freq(df, 'author_created_at', 'author_created_at', interval, 'ns')

    # stream twitter
    elif '_source.created_at' in df.columns:
        # default at 1 day
        if 'interval' in event:
            interval = event['interval']
        else:
            interval = '1D'
        freq = count_freq(df, '_source.created_at', '_source.created_at', interval, 'ns')
       
    # reddit, reddit post, reddit comment
    elif 'created_utc' in df.columns:
        # default at 1 month
        if 'interval' in event:
            interval = event['interval']
        else:
            interval = '1M'
        freq = count_freq(df, 'created_utc', 'created_utc', interval, 's')

    # historical reddit post
    elif '_source.created_utc' in df.columns:
        # default at 1 month
        if 'interval' in event:
            interval = event['interval']
        else:
            interval = '1M'
        freq = count_freq(df, '_source.created_utc', '_source.created_utc', interval, 's')

    # historical reddit comment
    elif 'comment_created' in df.columns:
        # default at 1 month
        if 'interval' in event:
            interval = event['interval']
        else:
            interval = '1M'
        freq = count_freq(df, 'comment_created', 'comment_created', interval, 's')   
    else:
        return {'url':'null'}

    index = freq.index.tolist()
    counts = freq.tolist()
    
    url = plot_freq(index, counts, interval, localPath, remotePath)
    print(url)

    return {'url': url}
        
    
