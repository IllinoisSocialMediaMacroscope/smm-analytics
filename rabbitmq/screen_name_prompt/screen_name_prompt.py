import tweepy
import json
import pika
from argparse import RawTextHelpFormatter, ArgumentParser


def screen_name_prompt_handler(ch, method, properties, body):

    event = json.loads(body)
    auth = tweepy.OAuthHandler(event['consumer_key'], event['consumer_secret'])
    auth.set_access_token(event['access_token'], event['access_token_secret'])
    api = tweepy.API(auth)

    users = api.search_users(q=event['screen_name'], per_page=20)

    # serialize User object
    users_list = []
    for user in users:
        users_list.append(user._json)

    # reply to the sender
    ch.basic_publish(exchange="",
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(users_list))

    return users_list


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
    queue = "bae_screen_name_prompt"
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=screen_name_prompt_handler, auto_ack=True)
    channel.start_consuming()