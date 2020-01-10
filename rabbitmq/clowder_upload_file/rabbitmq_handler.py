import json
import os
import traceback

import pika
import requests

# global
headers = {'Content-type': 'application/json', 'accept': 'application/json'}

def add_tags(fileID, auth, tags):
    payload = json.dumps({'tags': tags})
    r = requests.post('https://socialmediamacroscope.ncsa.illinois.edu/' +
                      'clowder/api/files/' + fileID + '/tags',
                      data=payload,
                      headers=headers,
                      auth=auth)
    if r.status_code != 200:
        return None


def add_descriptions(fileID, auth, descriptions):
    payload = json.dumps({'description': descriptions})
    r = requests.put('https://socialmediamacroscope.ncsa.illinois.edu/clowder' +
                     '/api/files/' + fileID + '/updateDescription',
                     data=payload,
                     headers=headers,
                     auth=auth)
    if r.status_code != 200:
        return None


def add_metadata(fileID, auth, metadata):
    payload = json.dumps(metadata)
    r = requests.post('https://socialmediamacroscope.ncsa.illinois.edu' +
                      '/clowder/api/files/' + fileID + '/metadata',
                      data=payload,
                      headers=headers,
                      auth=auth)
    if r.status_code != 200:
        return None

def get_config_json(config_url):
    # download config data to json
    r_config = requests.get(config_url)

    if r_config.status_code == 200:
        return r_config.json()
    else:
        return None


def rabbitmq_handler(ch, method, properties, body):
    try:
        # basic fields
        event = json.loads(body)
        # basic fields
        auth = (event['username'], event['password'])
        dataset_id = event['payload']['dataset_id']
        config_url = event['payload']['configuration']
        config_json = get_config_json(config_url)

        # loop through URL list
        file_id = []
        for url in event['payload'].keys():
            if url != 'dataset_id' and url != 'configuration':
                r = requests.post(
                    'https://socialmediamacroscope.ncsa.illinois.edu/clowder/api/datasets/' + dataset_id + '/urls',
                    data=json.dumps({'url': url}),
                    headers=headers,
                    auth=auth)
                if r.status_code != 200:
                    raise ValueError('cannot upload this file: ' + dataset_id)
                else:
                    file_id.append(r.json()['id'])

                    if 'tags' in event['payload'][url].keys():
                        if not add_tags(r.json()['id'], auth, event['payload'][url]['tags']):
                            raise ValueError('cannot add tags to this file: ' + r.json()['id'])

                    # add config file to metadata (default)
                    if not add_metadata(r.json()['id'], auth, config_json):
                        raise ValueError('cannot add config metadata to this file: ' + r.json()['id'])
                    if 'metadata' in event['payload'][url].keys():
                        if not add_metadata(r.json()['id'], auth, event['payload'][url]['metadata']):
                            raise ValueError('cannot add metadata to this file: ' + r.json()['id'])

                    if 'descriptions' in event['payload'][url].keys():
                        if not add_descriptions(r.json()['id'], auth, event['payload'][url]['descriptions']):
                            raise ValueError('cannot add tags to this file: ' + r.json()['id'])

        resp = {'info': 'You have successfully uploaded all the files to your specified dataset!',
                'ids': file_id}

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
