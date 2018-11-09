import tweepy
import os
import writeToS3 as s3

def lambda_handler(event, context):

	awsPath = os.path.join(event['sessionID'], event['screen_name'])
	localSavePath = os.path.join('/tmp', event['sessionID'], event['screen_name'])
	if not os.path.exists(localSavePath):
		os.makedirs(localSavePath)

	auth = tweepy.OAuthHandler(event['consumer_key'], event['consumer_secret'])
	auth.set_access_token(event['access_token'], event['access_token_secret'])
	api = tweepy.API(auth)

	tweets = []
	for status in tweepy.Cursor(api.user_timeline, screen_name=event['screen_name'],count=100).items():
		tweets.append(status._json['text'])

	if len(tweets) > 0:
		fname = event['screen_name'] + '_tweets.txt'
		with open(os.path.join(localSavePath, fname), 'w') as f:
			f.write('. '.join(tweets))

		s3.upload(localSavePath, awsPath, fname)

		return {'url': s3.generate_downloads(awsPath, fname)}
	else:
		raise ValueError('This user\'s timeline (screen_name: ' + event['screen_name'] +') is empty. There is nothing to analyze!')