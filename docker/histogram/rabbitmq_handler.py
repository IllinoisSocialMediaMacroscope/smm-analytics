import csv
import json
import os
import traceback

import pandas as pd
import pika
import writeToS3 as s3
from histogram import plot_freq, count_freq


def rabbitmq_handler(ch, method, properties, body):
    try:

        event = json.loads(body)
        # download the social media data to local lambda /tmp
        localPath = '/tmp/' + event['s3FolderName'] + '/'
        filename = event['filename']
        remotePath = event['remoteReadPath']

        if not os.path.exists(localPath):
            os.makedirs(localPath)

        s3.downloadToDisk(filename=filename, localpath=localPath, remotepath=remotePath)

        # read it into csv
        Array = []
        try:
            with open(localPath + filename, 'r', encoding="utf-8") as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        Array.append(row)
                except Exception as e:
                    pass
        except:
            with open(localPath + filename, 'r', encoding="ISO-8859-1") as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        Array.append(row)
                except Exception as e:
                    pass

        df = pd.DataFrame(Array[1:], columns=Array[0])
        # tweet
        if 'created_at' in df.columns:
            # default at 1 hour
            if 'interval' in event:
                interval = event['interval']
            else:
                interval = '1H'
            freq = count_freq(df, 'created_at', interval, 'ns')

        # twitter user
        elif 'author_created_at' in df.columns:
            # default at 1M
            if 'interval' in event:
                interval = event['interval']
            else:
                interval = '1M'
            freq = count_freq(df, 'author_created_at', interval, 'ns')

        # stream twitter
        elif '_source.created_at' in df.columns:
            # default at 1 day
            if 'interval' in event:
                interval = event['interval']
            else:
                interval = '1D'
            freq = count_freq(df, '_source.created_at', interval, 'ns')

        # reddit, reddit post, reddit comment
        elif 'created_utc' in df.columns:
            # default at 1 month
            if 'interval' in event:
                interval = event['interval']
            else:
                interval = '1M'
            freq = count_freq(df, 'created_utc', interval, 's')

        # historical reddit post
        elif '_source.created_utc' in df.columns:
            # default at 1 month
            if 'interval' in event:
                interval = event['interval']
            else:
                interval = '1M'
            freq = count_freq(df, '_source.created_utc', interval, 's')

        # historical reddit comment
        elif 'comment_created' in df.columns:
            # default at 1 month
            if 'interval' in event:
                interval = event['interval']
            else:
                interval = '1M'
            freq = count_freq(df, 'comment_created', interval, 's')

        # flickr photos
        elif 'info.dateuploaded' in df.columns:
            # default at 1 month
            if 'interval' in event:
                interval = event['interval']
            else:
                interval = '1M'
            freq = count_freq(df, 'info.dateuploaded', interval, 's')

        else:
            return {'url': 'null'}

        index = freq.index.tolist()
        counts = freq.tolist()

        urls = {'url': plot_freq(index, counts, interval, localPath, remotePath)}

    except BaseException as e:
        urls = {
            'ERROR':
                {
                    'message': str(e),
                    'traceback': traceback.format_exc()
                }
        }

        # reply to the sender
    ch.basic_publish(exchange="",
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(urls))

    return urls


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host="rabbitmq"))
    channel = connection.channel()

    # pass the queue name in environment variable
    queue = os.environ['QUEUE_NAME']

    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=rabbitmq_handler, auto_ack=True)
    channel.start_consuming()
