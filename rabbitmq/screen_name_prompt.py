import tweepy
import json
import pika


def screen_name_prompt_handler(ch, method, properties, body):

    event = json.loads(body)
    auth = tweepy.OAuthHandler(event['consumer_key'], event['consumer_secret'])
    auth.set_access_token(event['access_token'], event['access_token_secret'])
    api = tweepy.API(auth)

    users = api.search_users(q=event['screen_name'], per_page=20)

    # serialize User object
    users_list = []
    for user in users:
        users_list.append(user._json)

    # reply to the sender
    ch.basic_publish(exchange="",
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(users_list))

    return users_list


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
queue = "bae_screen_name_prompt"
channel.queue_declare(queue=queue)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue, on_message_callback=screen_name_prompt_handler, auto_ack=True)
channel.start_consuming()