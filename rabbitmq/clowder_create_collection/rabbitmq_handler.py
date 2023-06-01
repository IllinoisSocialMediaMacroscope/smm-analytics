import json
import os
import traceback

import pika
import requests

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')


def rabbitmq_handler(ch, method, properties, body):

    clowder_base_url = os.getenv('CLOWDER_BASE_URL', 'https://clowder.smm.ncsa.illinois.edu/')

    try:
        # basic fields
        event = json.loads(body)
        auth = (event['username'], event['password'])
        headers = {'Content-type': 'application/json', 'accept': 'application/json'}

        # create collection
        name = event['payload']['name']
        data = {'name': name}

        if 'descriptions' in event['payload'].keys():
            data['description'] = event['payload']['descriptions']
        if 'space' in event['payload'].keys():
            data['space'] = event['payload']['space']

        r = requests.post(clowder_base_url + 'api/collections',
                          data=json.dumps(data),
                          headers=headers,
                          auth=auth)
        if r.status_code != 200:
            resp = {'info': r.text, 'id': 'null'}
        else:
            resp = {'info': 'successfully created the new collection!', 'id': r.json()['id']}

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
