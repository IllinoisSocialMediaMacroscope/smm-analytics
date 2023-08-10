import json
import os
import traceback
import logging

import dataset
import pika
from algorithm import algorithm

import postToAWSLambda
import postToAWSBatch

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')


def rabbitmq_handler(ch, method, properties, body):
    try:
        msg = {}

        # determine if it goes to aws, lambda, or batch
        params = json.loads(body)

        if params['platform'] == 'aws-lambda':
            msg = postToAWSLambda.invoke(params['function_name'], params)

            # reply to the sender
            ch.basic_publish(exchange="",
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                             body=json.dumps(msg))

        elif params['platform'] == 'lambda':
            path = dataset.organize_path_lambda(params)

            # save the config file
            msg['config'] = dataset.save_remote_output(path['localSavePath'],
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
                    msg[key] = dataset.save_remote_output(path['localSavePath'],
                                                          path['remoteSavePath'],
                                                          key,
                                                          value)
                else:
                    msg[key] = value

            # reply to the sender
            ch.basic_publish(exchange="",
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                             body=json.dumps(msg))

        elif params['platform'] == 'aws-batch':
            postToAWSBatch.invoke(params['jobDefinition'],
                                        params['jobName'],
                                        params['jobQueue'],
                                        params['command'])

        elif params['platform'] == 'batch':
            os.system(' '.join(params['command']))

        else:
            raise ValueError(
                'Rabbitmq Message Not Recognizable. '
                'It has to specify what platform to run: aws-lambda, aws-batch, lambda or batch.')

    except Exception as e:
        logging.error(traceback.format_exc())
        msg = {'ERROR':
                   {'message': str(e),
                    'traceback': traceback.format_exc()
                    }
               }

        # reply to the sender
        ch.basic_publish(exchange="",
                         routing_key=properties.reply_to,
                         properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                         body=json.dumps(msg))

    return None


if __name__ == '__main__':
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        port=5672,
        host=RABBITMQ_HOST,
        heartbeat=600,
        blocked_connection_timeout=600,
        credentials=credentials
    ))
    channel = connection.channel()

    # pass the queue name in environment variable
    queue = os.environ['QUEUE_NAME']

    channel.queue_declare(queue=queue) #, arguments={'x-message-ttl': 1000 * 60 * 10}) # 10 minutes?
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=rabbitmq_handler, auto_ack=True)
    channel.start_consuming()
