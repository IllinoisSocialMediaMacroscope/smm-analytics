import json
import os
import traceback

import pika
import requests


def rabbitmq_handler(ch, method, properties, body):
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

        r = requests.post('https://socialmediamacroscope.ncsa.illinois.edu/clowder/api/collections',
                          data=json.dumps(data),
                          headers=headers,
                          auth=auth)

        print(r.status_code)
        print(r.text)

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
    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host="rabbitmq"))
    channel = connection.channel()

    # pass the queue name in environment variable
    queue = os.environ['QUEUE_NAME']

    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=rabbitmq_handler, auto_ack=True)
    channel.start_consuming()
