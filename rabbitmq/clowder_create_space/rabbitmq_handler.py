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

        # private method add user to space
        def _addUser(sp_id, usr_id, role):
            data = {'rolesandusers': {role: usr_id}}
            r = requests.post(
                'https://socialmediamacroscope.ncsa.illinois.edu/clowder/api/spaces/' + sp_id + '/updateUsers',
                data=json.dumps(data),
                headers=headers,
                auth=auth)
            if r.status_code != 200:
                return None
            else:
                return r.text

        # private method to identify myself
        def _findMyself(username):
            r = requests.get('https://socialmediamacroscope.ncsa.illinois.edu/clowder/api/me',
                             auth=auth)

            if r.status_code != 200:
                print('findMyself')
                print(r.text)
                return None
            else:
                return r.json()['id']

        # create collection
        name = event['payload']['name']
        data = {'name': name}

        if 'descriptions' in event['payload'].keys():
            data['description'] = event['payload']['descriptions']
        else:
            # important: description seems to be an required parameter
            data['description'] = ''

        r = requests.post('https://socialmediamacroscope.ncsa.illinois.edu/clowder/api/spaces',
                          data=json.dumps(data),
                          headers=headers,
                          auth=auth)

        if r.status_code != 200:
            resp = {'info': r.text, 'id': 'null'}

        else:
            resp = {'info': 'successfully created the new space!', 'id': r.json()['id']}

            # identify myself
            my_id = _findMyself(event['username'])

            if my_id == None:
                resp['info'] = 'cannot add yourself/person to this space, please to go clowder to add'

            # add myself as Admin
            if _addUser(r.json()['id'], my_id, 'Admin') == None:
                resp ['info'] = 'cannot add yourself/person to this space, please to go clowder to add'

            # add other people as Editor
            if 'usr_ids' in event['payload'].keys():
                if _addUser(r.json()['id'], event['payload']['usr_ids'], 'Editor') == None:
                    resp['info'] = 'cannot add yourself/person to this space, please to go clowder to add'


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
