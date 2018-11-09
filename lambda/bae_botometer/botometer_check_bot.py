import botometer
import json
import os
import writeToS3 as s3

def lambda_handler(event, context):
    mashape_key = event['mashape_key']
    twitter_app_auth = {
        'consumer_key': event['consumer_key'],
        'consumer_secret': event['consumer_secret'],
        'access_token': event['access_token'],
        'access_token_secret': event['access_token_secret'],
      }
    awsPath = os.path.join(event['session_id'], event['screen_name'])
    localSavePath = os.path.join('/tmp', event['session_id'],
                                 event['screen_name'])

    bom = botometer.Botometer(wait_on_ratelimit=False,
                          mashape_key=mashape_key,
                          **twitter_app_auth)
    result = bom.check_account(event['screen_name'])

    # save result in json file
    fname = event['screen_name'] + '_bot_score.txt'
    with open(os.path.join(localSavePath, fname), 'w') as f:
        json.dump(result, f)

    s3.upload(localSavePath, awsPath, fname)

    return result
