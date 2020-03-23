import tweepy
import json
import writeToS3 as s3
import os

def lambda_handler(event, context):
	
	auth = tweepy.OAuthHandler(event['consumer_key'], event['consumer_secret'])
	auth.set_access_token(event['access_token'], event['access_token_secret'])
	api = tweepy.API(auth)

	try:
		user = api.lookup_users(screen_names=[event['screen_name']])

		awsPath = os.path.join(event['sessionID'], event['screen_name'])
		localPath = os.path.join('/tmp', event['sessionID'], event['screen_name'])
		if not os.path.exists(localPath):
			os.makedirs(localPath)
		with open(os.path.join(localPath, event['screen_name'] + "_account_info.json"), "w") as f:
			json.dump(user[0]._json, f)
		s3.upload(localPath, awsPath, event['screen_name'] + "_account_info.json" )

		return {'user_exist': True,
				'profile_img': user[0]._json['profile_image_url_https'],
				'statuses_count': user[0]._json['statuses_count']}
	except tweepy.TweepError as error:
		return {'user_exist': False, 'profile_img': None, 'statuses_count': None}
