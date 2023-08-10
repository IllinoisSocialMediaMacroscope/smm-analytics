import json
import os
import traceback
import pika
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
            raise ValueError("Not applicable to this algorithm.")

        elif params['platform'] == 'lambda':
            raise ValueError("Not applicable to this algorithm.")

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

    except BaseException as e:

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

    queue = "bae_utku_brand_personality"
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=rabbitmq_handler, auto_ack=True)
    channel.start_consuming()
