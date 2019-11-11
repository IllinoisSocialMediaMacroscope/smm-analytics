import json
import pika
import tweepy
from argparse import RawTextHelpFormatter, ArgumentParser


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


if __name__ == '__main__':

    parser = ArgumentParser(formatter_class=RawTextHelpFormatter, description='Run consumer.py')
    parser.add_argument('--port', action='store', dest='port', help='The port to listen on.')
    parser.add_argument('--host', action='store', dest='host', help='The RabbitMQ host.')

    args = parser.parse_args()
    if not args.port:
        args.port = 5672
    if not args.host:
        raise ValueError("Missing required argument:--host")

    print(args.host)
    print(args.port)

    connection = pika.BlockingConnection(pika.ConnectionParameters(port=args.port, host=args.host))
    channel = connection.channel()
    queue = "bae_check_screen_name"
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=check_screen_name_handler, auto_ack=True)
    channel.start_consuming()
