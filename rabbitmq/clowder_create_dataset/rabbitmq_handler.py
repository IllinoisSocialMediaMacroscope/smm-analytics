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

        # create dataset
        title = event['payload']['title']
        data = {'name': title, 'access': 'PRIVATE'}

        if 'collection' in event['payload'].keys():
            data['collection'] = event['payload']['collection']
        if 'space' in event['payload'].keys():
            data['space'] = event['payload']['space']
        if 'descriptions' in event['payload'].keys():
            data['description'] = event['payload']['descriptions']

        r = requests.post('https://socialmediamacroscope.ncsa.illinois.edu/clowder/api/datasets/createempty',
                          data=json.dumps(data),
                          headers=headers,
                          auth=auth)
        if r.status_code != 200:
            resp = {'info': r.text, 'id': 'null'}
        else:

            dataset_id = r.json()['id']
            resp = {'info': 'successfully created the new dataset!', 'id': dataset_id }

            # if metadata exist, add metada
            if 'metadata' in event['payload'].keys():
                metadata = event['payload']['metadata']
                r = requests.post(
                    'https://socialmediamacroscope.ncsa.illinois.edu/clowder/api/datasets/' + dataset_id + '/metadata',
                    data=json.dumps(metadata),
                    headers=headers,
                    auth=auth)
                # if fail, return fail info and dataset id
                if r.status_code != 200:
                    resp['info'] = r.text

            # if tag exist, add tags
            if 'tags' in event['payload'].keys():
                tags = {'tags': event['payload']['tags']}
                r = requests.post(
                    'https://socialmediamacroscope.ncsa.illinois.edu/clowder/api/datasets/' + dataset_id + '/tags',
                    data=json.dumps(tags),
                    headers=headers,
                    auth=auth)
                # if fail, return fail info and dataset id
                if r.status_code != 200:
                    resp['info'] = r.text

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
