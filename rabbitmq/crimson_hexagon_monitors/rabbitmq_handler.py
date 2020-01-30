import json
import os
import traceback

import pika
import requests


def rabbitmq_handler(ch, method, properties, body):
    try:
        # important! Don't reveal this token
        event = json.loads(body)
        if 'crimson_access_token' in event.keys():
            crimson_auth_token = event['crimson_access_token']
            base_url = 'https://api.crimsonhexagon.com/api'

            url = base_url + '/monitor/list?auth=' + crimson_auth_token

            r = requests.get(url)

            if r.status_code != 200:
                data = {'info': r.text, 'monitor_list': 'null'}

            else:
                data = {'info': 'successfully retrieve monitor list!',
                        'monitor_list': r.json()['monitors']}
        else:
            data = {'info': 'You fail to provide the correct credentials to access Crimson Hexagon',
                    'monitor_list': 'null'}

    except BaseException as e:
        data = {
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
                     body=json.dumps(data))

    return data


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host="rabbitmq"))
    channel = connection.channel()

    # pass the queue name in environment variable
    queue = os.environ['QUEUE_NAME']

    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=rabbitmq_handler, auto_ack=True)
    channel.start_consuming()
