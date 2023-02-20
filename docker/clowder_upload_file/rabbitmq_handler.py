import json
import os
import traceback
from urllib.parse import urlparse

import pika
import requests
import writeToS3 as s3


def get_config_json(config_url):
    # download config data to json
    # parse url to extract filename, localPath, and awsPath
    path = urlparse(config_url).path.split('/')
    filename = path[-1]
    localPath = os.path.join('/tmp', path[2])
    if not os.path.exists(localPath):
        os.makedirs(localPath)
    awsPath = '/'.join(path[2:-1])
    try:
        s3.downloadToDisk(filename, localPath, awsPath)
    except:
        raise ValueError('Cannot find file:' + os.path.join(localPath, filename) + ' in the remote storage!')

    with open(os.path.join(localPath, filename), 'r') as f:
        return json.load(f)


def rabbitmq_handler(ch, method, properties, body):
    try:
        # basic fields
        event = json.loads(body)
        auth = (event['username'], event['password'])
        dataset_id = event['payload']['dataset_id']

        config_url = event['payload']['configuration']
        config_json = get_config_json(config_url)

        # upload files
        file_ids = []
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
            except:
                raise ValueError('Cannot find file:' + os.path.join(localPath, filename) + ' in the remote storage!')

            r = requests.post(
                'https://socialmediamacroscope.ncsa.illinois.edu/clowder/api/uploadToDataset/' + dataset_id +
                '?extract=true',
                files=[('File', open(os.path.join(localPath, filename), 'rb'))],
                auth=auth)

            if r.status_code != 200:
                raise ValueError("cannot upload these files to dataset: " +
                                 dataset_id + ". error:" + r.text)
            else:
                file_ids.append(r.json()['id'])

            # add config file to metadata (default)
            config_metadata_r = requests.post('https://socialmediamacroscope.ncsa.illinois.edu' +
                                              '/clowder/api/files/' + r.json()['id'] + '/metadata',
                                              data=json.dumps(config_json),
                                              headers={"Content-Type": "application/json"},
                                              auth=auth)
            if config_metadata_r.status_code != 200:
                raise ValueError('cannot add configuration metadata to this file: ' + r.json()['id'] + ". error: " +
                                 config_metadata_r.text)

            # add tags
            if 'tags' in file.keys():
                tag_payload = json.dumps({'tags': file['tags']})
                tag_r = requests.post('https://socialmediamacroscope.ncsa.illinois.edu/' +
                                      'clowder/api/files/' + r.json()['id'] + '/tags',
                                      data=tag_payload,
                                      headers={"Content-Type": "application/json"},
                                      auth=auth)
                if tag_r.status_code != 200:
                    raise ValueError('cannot add tags to this file: ' + r.json()['id'] + ". error: " + tag_r.text)

            # add metadata
            if 'metadata' in file.keys():
                metadata_payload = json.dumps(file['metadata'])
                metadata_r = requests.post('https://socialmediamacroscope.ncsa.illinois.edu' +
                                           '/clowder/api/files/' + r.json()['id'] + '/metadata',
                                           data=metadata_payload,
                                           headers={"Content-Type": "application/json"},
                                           auth=auth)
                if metadata_r.status_code != 200:
                    raise ValueError('cannot add metadata to this file: ' + r.json()['id'] + ". error: " +
                                     metadata_r.text)

            # add description
            if 'descriptions' in file.keys():
                description_payload = json.dumps({'description': file['descriptions']})
                description_r = requests.put('https://socialmediamacroscope.ncsa.illinois.edu/clowder' +
                                             '/api/files/' + r.json()['id'] + '/updateDescription',
                                             data=description_payload,
                                             headers={"Content-Type": "application/json"},
                                             auth=auth)
                if description_r.status_code != 200:
                    raise ValueError(
                        'cannot add descriptions to this file: ' + r.json()['id'] + ". error: " + description_r.text)

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
