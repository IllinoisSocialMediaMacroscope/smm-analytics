import json
import os
import traceback
import pika
import postToAWSBatch


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
    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host="rabbitmq", heartbeat=0))
    channel = connection.channel()

    # pass the queue name in environment variable
    queue = os.environ['QUEUE_NAME']

    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=rabbitmq_handler, auto_ack=True)
    channel.start_consuming()
