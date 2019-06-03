import tweepy


def lambda_handler(event, context=None):
    auth = tweepy.OAuthHandler(event['consumer_key'], event['consumer_secret'])
    auth.set_access_token(event['access_token'], event['access_token_secret'])
    api = tweepy.API(auth)

    users = api.search_users(q=event['screen_name'], per_page=20)

    # serialize User object
    users_list = []
    for user in users:
        users_list.append(user._json)

    return users_list

if __name__ == '__main__':
    # to test locally
    event = {
        "consumer_key":"xxx",
        "consumer_secret":"xxx",
        "access_token":"xxx",
        "access_token_secret":"xxx",
        "screen_name":"xxx"
    }
    users = lambda_handler(event)
    print(users)