import json
import os
import traceback

import dataset
import pika
from algorithm import algorithm


def rabbitmq_handler(ch, method, properties, body):
    '''
    entrance to invoke AWS lambda,
    variable params contains parameters passed in
    '''

    try:
        urls = {}

        # arranging the paths
        params = json.loads(body)
        path = dataset.organize_path_lambda(params)

        # save the config file
        urls['config'] = dataset.save_remote_output(path['localSavePath'],
                                                    path['remoteSavePath'],
                                                    'config',
                                                    params)
        # prepare input dataset
        df = dataset.get_remote_input(path['remoteReadPath'],
                                      path['filename'],
                                      path['localReadPath'])

        # execute the algorithm
        output = algorithm(df, params)

        # upload object to s3 bucket and return the url
        for key, value in output.items():
            if key != 'uid':
                urls[key] = dataset.save_remote_output(path['localSavePath'],
                                                       path['remoteSavePath'],
                                                       key,
                                                       value)
            else:
                urls[key] = value

    except BaseException as e:
        urls = {'ERROR':
                    {'message': str(e),
                     'traceback': traceback.format_exc()
                     }
                }

    # reply to the sender
    ch.basic_publish(exchange="",
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(urls))

    return urls


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host="rabbitmq"))
    channel = connection.channel()
    # pass the queue name in environment variable
    queue = os.environ['QUEUE_NAME']
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=rabbitmq_handler, auto_ack=True)
    channel.start_consuming()
