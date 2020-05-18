import writeToS3 as s3
import os
import tweepy
import csv
import time


def lambda_handler(event, context):

    screen_names = ["msalnacion", "gisbarbados", "MFABelize", "MinSaludBolivia", "minsaude", "GovCanHealth",
                    "caymangovt", "ministeriosalud", "MinSaludCol", "msaludcr", "GoDomRep", "Salud_Ec",
                    "ars_guyane", "MsppOfficiel", "themohwgovjm", "GobiernoMX", "msaludpy",
                    "PeruPaisDigital", "skngov", "MOH_TT", "MSPUruguay", "USAGov"]

    # create local path
    localPath = os.path.join('/tmp', 'tweets')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    # collect timeline
    auth = tweepy.OAuthHandler(os.environ['consumer_key'], os.environ['consumer_secret'])
    auth.set_access_token(os.environ['access_token'], os.environ['access_token_secret'])
    api = tweepy.API(auth)

    header = ["created_at",
              "id",
              "id_str",
              "full_text",
              "truncated",
              "display_text_range",
              "source",
              "in_reply_to_status_id",
              "in_reply_to_status_id_str",
              "in_reply_to_user_id",
              "in_reply_to_user_id_str",
              "in_reply_to_screen_name",
              "is_quote_status",
              "retweet_count",
              "favorite_count",
              "favorited",
              "retweeted",
              "possibly_sensitive",
              "lang"]

    for screen_name in screen_names:

        tweets = []
        for status in tweepy.Cursor(api.user_timeline, screen_name=screen_name, count=200,
                                    tweet_mode="extended").items():
            if "created_at" in status._json.keys() and status._json["created_at"][-4:] == "2020":
                tweet = []
                for key in header:
                    if key in status._json.keys():
                        # make sure date

                        if key == 'full_text':
                            tweet.append(status._json[key].encode('utf-8', 'ignore').decode())
                        else:
                            tweet.append(status._json[key])
                    else:
                        tweet.append("NA")
                tweets.append(tweet)
            else:
                break

        if len(tweets) > 0:
            fname = screen_name + '_tweets.csv'
            with open(os.path.join(localPath, fname), 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=",")
                writer.writerow(header)
                for row in tweets:
                    writer.writerow(row)

            s3.upload("macroscope-paho-covid", localPath, "input/twitter", fname)

            time.sleep(2)

    return None