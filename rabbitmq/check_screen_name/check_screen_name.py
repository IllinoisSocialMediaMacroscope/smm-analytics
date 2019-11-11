import json
import pika
import tweepy


def check_screen_name_handler(ch, method, properties, body):
    event = json.loads(body)
    auth = tweepy.OAuthHandler(event['consumer_key'], event['consumer_secret'])
    auth.set_access_token(event['access_token'], event['access_token_secret'])
    api = tweepy.API(auth)

    try:
        user = api.lookup_users(screen_names=[event['screen_name']])
        msg = {'user_exist': True, 'profile_img': user[0]._json['profile_image_url_https']}
    except tweepy.TweepError as error:
        msg = {'user_exist': False, 'profile_img': None}

    # reply to the sender
    ch.basic_publish(exchange="",
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(msg))

    return msg


connection = pika.BlockingConnection(pika.ConnectionParameters(port='5672'))
channel = connection.channel()
queue = "bae_check_screen_name"
channel.queue_declare(queue=queue)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue, on_message_callback=check_screen_name_handler, auto_ack=True)
channel.start_consuming()

