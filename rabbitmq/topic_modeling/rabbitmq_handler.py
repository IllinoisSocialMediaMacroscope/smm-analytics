import json
import os
import traceback
import pika


def rabbitmq_handler(ch, method, properties, body):
    '''
    entrance to invoke AWS lambda,
    variable params contains parameters passed in
    '''

    try:
        os.system(body)
        msg = {'command': body}
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

    return msg


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host="rabbitmq"))
    channel = connection.channel()

    # pass the queue name in environment variable
    queue = os.environ['QUEUE_NAME']
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=rabbitmq_handler, auto_ack=True)
    channel.start_consuming()
