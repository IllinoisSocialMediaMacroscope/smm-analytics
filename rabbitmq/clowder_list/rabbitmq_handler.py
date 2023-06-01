import json
import os
import traceback

import pika
import requests

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')


def rabbitmq_handler(ch, method, properties, body):

    clowder_base_url = os.getenv('CLOWDER_BASE_URL', 'https://clowder.smm.ncsa.illinois.edu/')
    clowder_global_key = os.getenv('CLOWDER_GLOBAL_KEY', "")

    try:
        # basic fields
        event = json.loads(body)
        auth = (event['username'], event['password'])

        if event['item'] == 'dataset':
            r = requests.get(clowder_base_url + 'api/datasets/canEdit', auth=auth)
        elif event['item'] == 'collection':
            r = requests.get(clowder_base_url + 'api/collections/canEdit', auth=auth)
        elif event['item'] == 'space':
            r = requests.get(clowder_base_url + 'api/spaces/canEdit', auth=auth)
        # use a global key here be careful of this information!!
        elif event['item'] == 'user':
            r = requests.get(clowder_base_url + 'api/users?key=' + clowder_global_key, auth=auth)
        else:
            return {'info': 'cannot list ' + event['item'], 'data': ['error']}

        if r.status_code != 200:
            resp = {'info': r.text, 'data': ['error']}
        else:
            resp = {'info': 'successfully fetched list of dataset', 'data': r.json()}

    except BaseException as e:
        resp = {
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
                     body=json.dumps(resp))

    return resp


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host=RABBITMQ_HOST))
    channel = connection.channel()

    # pass the queue name in environment variable
    queue = os.environ['QUEUE_NAME']

    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=rabbitmq_handler, auto_ack=True)
    channel.start_consuming()
