import json
import os
import pika
import tweepy
import writeToS3 as s3


def collect_timeline_handler(ch, method, properties, body):
    event = json.loads(body)
    awsPath = os.path.join(event['sessionID'], event['screen_name'])
    localSavePath = os.path.join('/tmp', event['sessionID'], event['screen_name'])
    if not os.path.exists(localSavePath):
        os.makedirs(localSavePath)

    auth = tweepy.OAuthHandler(event['consumer_key'], event['consumer_secret'])
    auth.set_access_token(event['access_token'], event['access_token_secret'])
    api = tweepy.API(auth)

    tweets = []
    for status in tweepy.Cursor(api.user_timeline, screen_name=event['screen_name'], count=100).items():
        tweets.append(status._json['text'].encode('utf-8', 'ignore').decode())

    if len(tweets) > 0:
        fname = event['screen_name'] + '_tweets.txt'
        with open(os.path.join(localSavePath, fname), 'w') as f:
            f.write('. '.join(tweets))

        s3.upload(localSavePath, awsPath, fname)

        data = {'url': s3.generate_downloads(awsPath, fname)}

        # reply to the sender
        ch.basic_publish(exchange="",
                         routing_key=properties.reply_to,
                         properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                         body=json.dumps(data))

        return data
    else:
        raise ValueError(
            'This user\'s timeline (screen_name: ' + event['screen_name'] + ') is empty. There is nothing to analyze!')


connection = pika.BlockingConnection(pika.ConnectionParameters(host='host.docker.internal'))
channel = connection.channel()
queue = "bae_collect_timeline"
channel.queue_declare(queue=queue)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue, on_message_callback=collect_timeline_handler, auto_ack=True)
channel.start_consuming()
