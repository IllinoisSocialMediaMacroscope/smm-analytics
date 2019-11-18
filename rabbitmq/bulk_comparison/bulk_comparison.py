import json
import os
import numpy as np
import pika


def cos_sim(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)


def bulk_comparison_handler(ch, method, properties, body):
    event = json.loads(body)
    localSavePath = os.path.join('/tmp', event['sessionID'])
    if not os.path.exists(localSavePath):
        raise ValueError('The current session doesn\'t exist!')

    # default algorithm to IBM-Watson to be compatible with old version
    if 'algorithm' not in event.keys():
        event['algorithm'] = 'IBM-Personality'

    comparison_table = [[]]

    # download and read personality scores
    if event['algorithm'] == 'IBM-Personality':
        comparison_table = [['screen_name', 'Personality_Openness',
                             'Personality_Conscientiousness',
                             'Personality_Extraversion',
                             'Personality_Agreeableness',
                             'Personality_Emotional_Range',
                             'Needs_Challenge', 'Needs_Closeness',
                             'Needs_Curiosity', 'Needs_Excitement',
                             'Needs_Harmony',
                             'Needs_Ideal', 'Needs_Liberty', 'Needs_Love',
                             'Needs_Practicality', 'Needs_Self_Expression',
                             'Needs_Stability', 'Needs_Structure',
                             'Values_Conservation', 'Values_Openness',
                             'Values_Hedonism', 'Values_Self_Enhancement',
                             'Values_Self_Transcendence']]

        for screen_name in event['screen_names']:
            personality = os.path.join(localSavePath, screen_name, "_personality.json")
            if not os.path.exists(personality):
                raise ValueError('Cannot find the personality in the remote storage!')
            else:
                with open(personality, 'r') as f:
                    data = json.load(f)['personality']
                    user_info = [screen_name]
                    for p in data['personality']:
                        user_info.append(p['percentile'])
                    for p in data['needs']:
                        user_info.append(p['percentile'])
                    for p in data['values']:
                        user_info.append(p['percentile'])
                    comparison_table.append(user_info)
    else:
        raise ValueError('Algorithm ' + event['algorithm'] + ' does not exist!')

    # computer correlations
    event['screen_names'].insert(0, 'Correlation')
    correlation_matrix = [event['screen_names']]
    correlation_matrix_no_legends = []
    for i in range(1, len(comparison_table)):
        row = [comparison_table[i][0]]
        row_no_legends = []

        for j in range(1, len(comparison_table)):
            vector_a = comparison_table[i][1:]
            vector_b = comparison_table[j][1:]

            row.append(cos_sim(vector_a, vector_b))
            row_no_legends.append(cos_sim(vector_a, vector_b))

        correlation_matrix.append(row)
        correlation_matrix_no_legends.append(row_no_legends)

    data = {'comparison_table': comparison_table,
            'correlation_matrix': correlation_matrix,
            'correlation_matrix_no_legends': correlation_matrix_no_legends}

    # reply to the sender
    ch.basic_publish(exchange="",
                     routing_key=properties.reply_to,
                     properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                     body=json.dumps(data))

    return data


if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters(port=5672, host="rabbitmq"))
    channel = connection.channel()
    queue = "bae_bulk_comparison"
    channel.queue_declare(queue=queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=bulk_comparison_handler, auto_ack=True)
    channel.start_consuming()