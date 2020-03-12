import numpy as np
import os
import json
import writeToS3 as s3

def cos_sim(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    return dot_product / (norm_a * norm_b)

def lambda_handler(event, context):

    awsUserPath = os.path.join(event['sessionID'], event['user_screen_name'])
    awsBrandPath = os.path.join(event['sessionID'], event['brand_screen_name'])
    localPath = os.path.join('/tmp', event['sessionID'])

    if not os.path.exists(localPath):
        os.makedirs(localPath)

    # default algorithm to IBM-Watson to be compatible with old version
    if 'algorithm' not in event.keys():
        event['algorithm'] =  'IBM-Watson'

    # calculate similarity score
    vector_a = []
    vector_b = []

    # download and read personality scores
    if event['algorithm'] == 'IBM-Watson':
        try:
            s3.downloadToDisk(event['user_screen_name'] + '_personality.json', localPath, awsUserPath)
            s3.downloadToDisk(event['brand_screen_name'] + '_personality.json', localPath, awsBrandPath)

            # open json and read in values
            with open(os.path.join(localPath, event['user_screen_name'] + '_personality.json'), 'r') as f:
                user_data = json.load(f)['personality']
            with open(os.path.join(localPath, event['brand_screen_name'] + '_personality.json'),'r') as f:
                brand_data = json.load(f)['personality']

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
        except:
            raise ValueError('Cannot find the timeline in the remote storage!')

    elif event['algorithm'] == 'TwitPersonality':
        try:
            s3.downloadToDisk(event['user_screen_name'] + '_twitPersonality.json', localPath, awsUserPath)
            s3.downloadToDisk(event['brand_screen_name'] + '_twitPersonality.json', localPath, awsBrandPath)

            # open json and read in values
            with open(os.path.join(localPath, event['user_screen_name'] + '_twitPersonality.json'), 'r') as f:
                user_data = json.load(f)['personality']
            with open(os.path.join(localPath, event['brand_screen_name'] + '_twitPersonality.json'),'r') as f:
                brand_data = json.load(f)['personality']

            if event['option'] == 'personality_sim_score':
                for p in user_data['personality']:
                    vector_a.append(p['percentile'])
                for p in brand_data['personality']:
                    vector_b.append(p['percentile'])

        except:
            raise ValueError('Cannot find the timeline in the remote storage!')

    if event['algorithm'] == 'Pamuksuz-Personality':
        try:
            s3.downloadToDisk(event['user_screen_name'] + '_utku_personality_average.json', localPath, awsUserPath)
            s3.downloadToDisk(event['brand_screen_name'] + '_utku_personality_average.json', localPath, awsBrandPath)

            # open json and read in values
            with open(os.path.join(localPath, event['user_screen_name'] + '_utku_personality_average.json'), 'r') as f:
                user_data = json.load(f)
            with open(os.path.join(localPath, event['brand_screen_name'] + '_utku_personality_average.json'), 'r') as f:
                brand_data = json.load(f)

            for metric in user_data.keys():
                vector_a.append(user_data[metric])
                vector_b.append(brand_data[metric])
        except:
            raise ValueError('Cannot find the timeline in the remote storage!')

    try:
        return {'sim_score': cos_sim(vector_a, vector_b)}
    except:
        raise ValueError(
            'cannot calculate the cosine similarity of these two vectors!')
