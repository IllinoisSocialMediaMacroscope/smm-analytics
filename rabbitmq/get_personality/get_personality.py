import json
import os
import pika
import requests
import writeToS3 as s3
from argparse import RawTextHelpFormatter, ArgumentParser


def get_personality_handler(ch, method, properties, body):
    event = json.loads(body)
    awsPath = os.path.join(event['sessionID'], event['screen_name'])
    localPath = os.path.join('/tmp', event['sessionID'], event['screen_name'])
    if not os.path.exists(localPath):
        os.makedirs(localPath)
    screen_name = event['screen_name']

    try:
        s3.downloadToDisk(screen_name + '_tweets.txt', localPath, awsPath)
    except:
        raise ValueError('Cannot find the timeline in the remote storage!')

    with open(os.path.join(localPath, screen_name + '_tweets.txt'), 'r') as personality_text:
        headers = {'Content-Type': 'text/plain',
                   'Accept': 'application/json'}
        body = personality_text.read().encode('utf-8', 'ignore')
        r = requests.post(
            'https://gateway.watsonplatform.net/personality-insights/api/v3/profile?version=2017-10-13&consumption_preferences=true&raw_scores=true',
            headers=headers, data=body, auth=('apikey', event['apikey']), timeout=300)

        if r.status_code == 200:
            data = {'screen_name': screen_name,
                    'profile_img': event['profile_img'],
                    'personality': r.json()}

            with open(os.path.join(localPath, screen_name + '_personality' + '.json'), 'w') as outfile:
                json.dump(data, outfile)

            s3.upload(localPath, awsPath, screen_name + '_personality.json')

            # reply to the sender
            ch.basic_publish(exchange="",
                             routing_key=properties.reply_to,
                             properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                             body=json.dumps(data))

            return data
        else:
            raise ValueError(r.text)


if __name__ == '__main__':

    parser = ArgumentParser(formatter_class=RawTextHelpFormatter, description='Run consumer.py')
    parser.add_argument('--port', action='store', dest='port', help='The port to listen on.')
    parser.add_argument('--host', action='store', dest='host', help='The RabbitMQ host.')

    args = parser.parse_args()
    if not args.port:
        args.port = 5672
    if not args.host:
        raise ValueError("Missing required argument:--host")

    print(args.host)
    print(args.port)

    connection = pika.BlockingConnection(pika.ConnectionParameters(port=args.port, host=args.host))
    channel = connection.channel()
    queue = "bae_get_personality"
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=get_personality_handler, auto_ack=True)
    channel.start_consuming()
