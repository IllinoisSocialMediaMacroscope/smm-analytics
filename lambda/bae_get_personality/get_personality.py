import os
import json
import requests
import writeToS3 as s3
import pandas as pd

def lambda_handler(event, context):

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

        # concatenate the text field to be a paragraph
        df = pd.read_csv(os.path.join(localPath, screen_name + '_tweets.txt'))
        tweets = df['text'].tolist()
        body = '. '.join(tweets).encode('utf-8', 'ignore')

        r = requests.post('https://gateway.watsonplatform.net/personality-insights/api/v3/profile?version=2017-10-13&consumption_preferences=true&raw_scores=true',
            headers=headers, data=body, auth=('apikey', event['apikey']), timeout=300)

        if r.status_code == 200:
            data = { 'personality': r.json()}

            with open(os.path.join(localPath, screen_name + '_personality' + '.json'),'w') as outfile:
                json.dump(data, outfile)

            s3.upload(localPath, awsPath, screen_name + '_personality.json')

            return data
        else:
            raise ValueError(r.text)


