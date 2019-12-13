import json
import botometer
import pika
import traceback


def botometer_check_bot_handler(ch, method, properties, body):

    try:
        event = json.loads(body)
        mashape_key = event['mashape_key']
        twitter_app_auth = {
            'consumer_key': event['consumer_key'],
            'consumer_secret': event['consumer_secret'],
            'access_token': event['access_token'],
            'access_token_secret': event['access_token_secret'],
        }
        bom = botometer.Botometer(wait_on_ratelimit=False,
                                  mashape_key=mashape_key,
                                  **twitter_app_auth)
        result = bom.check_account(event['screen_name'])
    except BaseException as e:
        result = {'ERROR':
                      {'message': str(e),
                       'traceback': traceback.format_exc()
                       }
                  }

    # reply to the sender
    ch.basic_publish(exchange="",
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(result))

    return result


if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host="rabbitmq"))
    channel = connection.channel()
    queue = "bae_botometer"
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=botometer_check_bot_handler, auto_ack=True)
    channel.start_consuming()
