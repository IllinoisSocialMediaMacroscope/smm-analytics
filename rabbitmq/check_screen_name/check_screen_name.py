import json
import os
import pika
import tweepy
import traceback
import writeToS3 as s3


def check_screen_name_handler(ch, method, properties, body):
    try:
        event = json.loads(body)
        auth = tweepy.OAuthHandler(event['consumer_key'], event['consumer_secret'])
        auth.set_access_token(event['access_token'], event['access_token_secret'])
        api = tweepy.API(auth)

        try:
            user = api.lookup_users(screen_names=[event['screen_name']])

            awsPath = os.path.join(event['sessionID'], event['screen_name'])
            localPath = os.path.join('/tmp', event['sessionID'], event['screen_name'])
            if not os.path.exists(localPath):
                os.makedirs(localPath)
            with open(os.path.join(localPath, event['screen_name'] + "_account_info.json"), "w") as f:
                json.dump(user[0]._json, f)
            s3.upload(localPath, awsPath, event['screen_name'] + "_account_info.json")

            msg = {'user_exist': True,
                   'profile_img': user[0]._json['profile_image_url_https'],
                   'statuses_count': user[0]._json['statuses_count']}
        except tweepy.TweepError as error:
            msg = {'user_exist': False, 'profile_img': None, 'statuses_count': None}

    except BaseException as e:
        msg = {'ERROR':
            {
                'message': str(e),
                'traceback': traceback.format_exc()
            }
        }

    # reply to the sender
    ch.basic_publish(exchange="",
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(msg))

    return msg


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host="rabbitmq"))
    channel = connection.channel()
    queue = "bae_check_screen_name"
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=check_screen_name_handler, auto_ack=True)
    channel.start_consuming()
