import tweepy

def lambda_handler(event, context):
	
	auth = tweepy.OAuthHandler(event['consumer_key'], event['consumer_secret'])
	auth.set_access_token(event['access_token'], event['access_token_secret'])
	api = tweepy.API(auth)

	try:
		user = api.lookup_users(screen_names=[event['screen_name']])
		return {'user_exist': True,
				'profile_img': user[0]._json['profile_image_url_https'],
				'statuses_count': user[0]._json['statuses_count']}
	except tweepy.TweepError as error:
		return {'user_exist': False, 'profile_img': None, 'statuses_count': None}
