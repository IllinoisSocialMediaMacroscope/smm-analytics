import json
import botometer
import pika
from argparse import RawTextHelpFormatter, ArgumentParser


def botometer_check_bot_handler(ch, method, properties, body):
    event = json.loads(body)
    mashape_key = event['mashape_key']
    twitter_app_auth = {
        'consumer_key': event['consumer_key'],
        'consumer_secret': event['consumer_secret'],
        'access_token': event['access_token'],
        'access_token_secret': event['access_token_secret'],
    }
    bom = botometer.Botometer(wait_on_ratelimit=False,
                              mashape_key=mashape_key,
                              **twitter_app_auth)
    result = bom.check_account(event['screen_name'])

    # reply to the sender
    ch.basic_publish(exchange="",
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(result))

    return result


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
    queue = "bae_botometer"
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=botometer_check_bot_handler, auto_ack=True)
    channel.start_consuming()
