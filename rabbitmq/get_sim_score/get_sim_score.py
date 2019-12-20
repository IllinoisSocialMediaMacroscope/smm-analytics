import json
import os
import numpy as np
import pika


def cos_sim(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    return dot_product / (norm_a * norm_b)

def get_sim_score_handler(ch, method, properties, body):
    event = json.loads(body)
    localSavePath = os.path.join('/tmp', event['sessionID'])
    if not os.path.exists(localSavePath):
        raise ValueError('The current session doesn\'t exist!')

    user_personality = os.path.join(localSavePath, event['user_screen_name'], event['user_screen_name'] +
    '_personality.json')
    brand_personality = os.path.join(localSavePath, event['brand_screen_name'], event['brand_screen_name'] +
    '_personality.json')

    # default algorithm to IBM-Watson to be compatible with old version
    if 'algorithm' not in event.keys():
        event['algorithm'] = 'IBM-Watson'

    # download and read personality scores
    if event['algorithm'] == 'IBM-Watson':

        if not os.path.exists(user_personality) or not os.path.exists(brand_personality):
            raise ValueError('Cannot find the personalities in the storage!')
        else:
            # open json and read in values
            with open(user_personality, 'r') as f:
                user_data = json.load(f)['personality']
            with open(brand_personality, 'r') as f:
                brand_data = json.load(f)['personality']
    else:
        raise ValueError('Algorithm ' + event['algorithm'] + ' does not exist!')

    # calculate similarity score
    vector_a = []
    vector_b = []
    if event['option'] == 'personality_sim_score':
        for p in user_data['personality']:
            vector_a.append(p['percentile'])
        for p in brand_data['personality']:
            vector_b.append(p['percentile'])

    elif event['option'] == 'needs_sim_score':
        for p in user_data['needs']:
            vector_a.append(p['percentile'])
        for p in brand_data['needs']:
            vector_b.append(p['percentile'])

    elif event['option'] == 'values_sim_score':
        for p in user_data['values']:
            vector_a.append(p['percentile'])
        for p in brand_data['values']:
            vector_b.append(p['percentile'])
    elif event['option'] == 'consumption_sim_score':
        for p in user_data['consumption_preferences']:
            for c in p['consumption_preferences']:
                vector_a.append(c['score'])
        for p in brand_data['consumption_preferences']:
            for c in p['consumption_preferences']:
                vector_b.append(c['score'])

    try:
        data = {'sim_score': cos_sim(vector_a, vector_b)}
        # reply to the sender
        ch.basic_publish(exchange="",
                         routing_key=properties.reply_to,
                         properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                         body=json.dumps(data))
        return data
    except:
        raise ValueError(
            'cannot calculate the cosine similarity of these two vectors!')


if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host="rabbitmq"))
    channel = connection.channel()
    queue = "bae_get_sim_score"
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=get_sim_score_handler, auto_ack=True)
    channel.start_consuming()