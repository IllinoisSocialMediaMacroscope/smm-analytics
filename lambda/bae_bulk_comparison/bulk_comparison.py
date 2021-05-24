import os
import json
import writeToS3 as s3
import numpy as np


def cos_sim(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)

def lambda_handler(event, context):

    localPath = os.path.join('/tmp', event['sessionID'])
    if not os.path.exists(localPath):
        os.makedirs(localPath)

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
            awsPath = os.path.join(event['sessionID'], screen_name)
            try:
                s3.downloadToDisk(screen_name + '_personality.json', localPath, awsPath)
            except:
                raise ValueError('Cannot find the personality in the remote storage!')

            with open(os.path.join(localPath, screen_name + '_personality.json'), 'r') as f:
                data = json.load(f)['personality']
                user_info = [screen_name]
                for p in data['personality']:
                    user_info.append(p['percentile'])
                for p in data['needs']:
                    user_info.append(p['percentile'])
                for p in data['values']:
                    user_info.append(p['percentile'])
                comparison_table.append(user_info)

    elif event['algorithm'] == 'TwitPersonality':
        comparison_table = [['screen_name', 'Personality_Openness',
                             'Personality_Conscientiousness',
                             'Personality_Extraversion',
                             'Personality_Agreeableness',
                             'Personality_Emotional_Range']]

        for screen_name in event['screen_names']:
            awsPath = os.path.join(event['sessionID'], screen_name)
            try:
                s3.downloadToDisk(screen_name + '_twitPersonality.json', localPath, awsPath)
            except:
                raise ValueError('Cannot find the personality in the remote storage!')

            with open(os.path.join(localPath, screen_name + '_twitPersonality.json'), 'r') as f:
                data = json.load(f)['personality']
                user_info = [screen_name]
                for p in data['personality']:
                    user_info.append(p['percentile'])
                comparison_table.append(user_info)

    elif event['algorithm'] == 'Pamuksuz-Personality':
        comparison_table = [['screen_name', 'sophistication',
                             'excitement', 'sincerity',
                             'competence', 'ruggedness'
                             ]]
        for screen_name in event['screen_names']:
            awsPath = os.path.join(event['sessionID'], screen_name)
            try:
                s3.downloadToDisk(screen_name + '_utku_personality_average.json', localPath, awsPath)
            except:
                raise ValueError('Cannot find the personality in the remote storage!')

            with open(os.path.join(localPath, screen_name + '_utku_personality_average.json'), 'r') as f:
                data = json.load(f)
                comparison_table.append([screen_name, data['sophistication'], data['excitement'], data['sincerity'],
                                  data['competence'], data['ruggedness']])

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

    return {'comparison_table':comparison_table,
            'correlation_matrix':correlation_matrix,
            'correlation_matrix_no_legends':correlation_matrix_no_legends}

