import botometer
import os

def lambda_handler(event, context):
    twitter_app_auth = {
        'consumer_key': event['consumer_key'],
        'consumer_secret': event['consumer_secret'],
        'access_token': event['access_token'],
        'access_token_secret': event['access_token_secret'],
      }
    bom = botometer.Botometer(wait_on_ratelimit=False,
                          mashape_key=os.environ.get("rapidapi_key"),
                          **twitter_app_auth)
    result = bom.check_account(event['screen_name'])

    return result