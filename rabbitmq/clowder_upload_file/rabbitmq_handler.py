import json
import os
import traceback

import pika
import requests
import writeToS3 as s3
from urllib.parse import urlparse


def add_tags(fileID, auth, tags):
    headers = {'Content-type': 'application/json', 'accept': 'application/json'}
    payload = json.dumps({'tags': tags})
    r = requests.post('https://socialmediamacroscope.ncsa.illinois.edu/' +
                      'clowder/api/files/' + fileID + '/tags',
                      data=payload,
                      headers=headers,
                      auth=auth)
    if r.status_code != 200:
        return None


def add_descriptions(fileID, auth, descriptions):
    headers = {'Content-type': 'application/json', 'accept': 'application/json'}
    payload = json.dumps({'description': descriptions})
    r = requests.put('https://socialmediamacroscope.ncsa.illinois.edu/clowder' +
                     '/api/files/' + fileID + '/updateDescription',
                     data=payload,
                     headers=headers,
                     auth=auth)
    if r.status_code != 200:
        return None


def add_metadata(fileID, auth, metadata):
    headers = {'Content-type': 'application/json', 'accept': 'application/json'}
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
        headers = {"Content-Type":"multipart/form-data"}
        auth = (event['username'], event['password'])
        dataset_id = event['payload']['dataset_id']

        # config_url = event['payload']['configuration']
        # config_json = get_config_json(config_url)

        files = []
        for file in event['payload']['files']:

            # parse url to extract filename, localPath, and awsPath
            path = urlparse(file['url']).path.split('/')
            filename = path[-1]
            localPath = os.path.join('/tmp', path[2])
            if not os.path.exists(localPath):
                os.makedirs(localPath)
            awsPath = '/'.join(path[2:-1])
            try:
                s3.downloadToDisk(filename, localPath, awsPath)
                files.append(('File', open(os.path.join(localPath, filename), 'rb')))
            except:
                raise ValueError('Cannot find file:' + os.path.join(awsPath, filename) + ' in the remote storage!')

        r = requests.post(
            'https://socialmediamacroscope.ncsa.illinois.edu/clowder/api/uploadToDataset/' + dataset_id +
            '?extract=true',
            files = files,
            headers=headers,
            auth=auth)

        if r.status_code != 200:
            raise ValueError('cannot upload this file: ' + dataset_id)
        else:
            file_ids = r.json()['ids']

            # if 'tags' in event['payload'][url].keys():
            #     if not add_tags(r.json()['id'], auth, event['payload'][url]['tags']):
            #         raise ValueError('cannot add tags to this file: ' + r.json()['id'])
            # # add config file to metadata (default)
            # if not add_metadata(r.json()['id'], auth, config_json):
            #     raise ValueError('cannot add config metadata to this file: ' + r.json()['id'])
            # if 'metadata' in event['payload'][url].keys():
            #     if not add_metadata(r.json()['id'], auth, event['payload'][url]['metadata']):
            #         raise ValueError('cannot add metadata to this file: ' + r.json()['id'])
            #
            # if 'descriptions' in event['payload'][url].keys():
            #     if not add_descriptions(r.json()['id'], auth, event['payload'][url]['descriptions']):
            #         raise ValueError('cannot add tags to this file: ' + r.json()['id'])

        resp = {'info': 'You have successfully uploaded all the files to your specified dataset!',
                'ids': file_ids}

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
