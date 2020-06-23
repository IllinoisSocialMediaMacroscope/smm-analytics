'''
Created on Mar 22, 2018
Edited on Nov 19, 2019

@author: npvance2
@author: curtisd2
'''

import csv
import json
import os
import urllib.request
from datetime import date, timedelta

import tweepy
import writeToS3 as s3
from tweepy import OAuthHandler


def getAuthToken():  # provides auth token needed to access Crimson API
    authToken = os.environ['brandwatchAuthToken']
    authToken = "&access_token=" + authToken
    return authToken


def twitterAPI():  # Provides access keys for Twitter API
    consumer_key = os.environ['consumer_key']
    consumer_secret = os.environ['consumer_secret']
    access_token = os.environ['access_token']
    access_token_secret = os.environ['access_token_secret']

    if (consumer_key == '') or (consumer_secret == '') or (access_token == '') or (access_token_secret == ''):
        print("Not all Twitter keys have been entered, please add them to the script and try again")
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api


def DatePull(startdate, enddate):
    listArray = []
    startdate = date(int(startdate[0:4]), int(startdate[5:7]), int(startdate[8:10]))
    enddate = date(int(enddate[0:4]), int(enddate[5:7]), int(enddate[8:10]))

    while startdate <= enddate:
        listArray.append(str(startdate))
        startdate += timedelta(days=1)
    return listArray


def collect_crimson_monitor_data(projectStartDate, projectEndDate, localPath):
    monitorID = 'queryId=' + os.environ['monitorID']
    fname = "Monitor-" + monitorID + '-from-' + projectStartDate + '-to-' + projectEndDate + '.csv'
    lineArray = DatePull(projectStartDate, projectEndDate)

    urlStart = "https://api.brandwatch.com"

    # write header
    with open(os.path.join(localPath, fname), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ["PostType", "PostDate", "PostTime", "URL", "TweetID", "Contents", "RetweetCount", "FavoriteCount",
                  "Location", "Language", "Sentiment", "NeutralScore", "PositiveScore", "NegativeScore", "Followers",
                  "Friends", "Author", "AuthorGender", "AuthorTweets"]
        writer.writerow(header)

    for i in range(len(lineArray) - 1):
        startDate = lineArray[i]
        endDate = lineArray[i + 1]

        dates = "&startDatae=" + startDate + "&endDate=" + endDate  # Combines start and end date into format needed
        # for API call
        authToken = getAuthToken()  # Gets auth token
        endpoint = "/projects/1998292854/data/mentions/fulltext?"  # endpoint needed for this query
        urlData = urlStart + endpoint + monitorID + authToken + dates # Combines all API calls parts into full URL

        webURL = urllib.request.urlopen(urlData)

        if webURL.getcode() == 200:
            # write body
            with open(os.path.join(localPath, fname), 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                data = webURL.read().decode('utf8')
                theJSON = json.loads(data)

                postDates = []  # These initialize the attributes of the final output
                postTimes = []
                urls = []
                contents = []
                authors = []
                authorGenders = []
                locations = []
                languages = []
                postTypes = []
                sentiments = []
                neutralScore = []
                positiveScore = []
                negativeScore = []
                tweetIDs = []
                followers = []
                friends = []
                retweetCounts = []
                favoritesCount = []
                statusesCount = []
                tweetCount = 0
                tempTweetIDs = []

                api = twitterAPI()
                c = 0

                for i in theJSON["posts"]:
                    postDates.append("")
                    postTimes.append("")

                    if ('date' in i):  # identifies date posted
                        tempDate = str(i["date"])
                        dateTime = tempDate.split("T")
                        postDates[c] = dateTime[0]
                        postTimes[c] = dateTime[1]

                    urls.append(i["url"])

                    contents.append("")
                    if ('fullText' in i and i['fullText'] is not None and len(i['fullText']) < 2000):
                        contents[c] = i['fullText'].replace(",", "").replace("\n", " ")
                    elif ('snippet' in i and i['snippet'] is not None):  # identifies post contents
                        contents[c] = i["snippet"].replace(",", "").replace("\n",
                                                                            " ")  # replaces commas and new lines to facilitate CSV formatting, this occasionally missed new lines in some blog posts which I'm working to fix

                    authors.append("")
                    if ('fullname' in i and i['fullname'] is not None):  # identifies author
                        authors[c] = i["fullname"].replace(",", "")

                    authorGenders.append("")
                    if ('Gender' in i and i['Gender'] is not None):  # identifies author gender
                        authorGenders[c] = i["Gender"]

                    locations.append("")
                    if ('locationName' in i and i['locationName'] is not None):  # identifies location
                        locations[c] = i["locationName"].replace(",", "")

                    languages.append("")
                    if ('language' in i and i[
                        'language'] is not None):  # identifies language specified in the author's profile
                        languages[c] = i["language"]

                    postTypes.append(i["pageType"])  # identifies the type of post, i.e. Twitter, Tumblr, Blog

                    tweetIDs.append("")

                    followers.append("")

                    friends.append("")

                    retweetCounts.append("")

                    favoritesCount.append("")

                    statusesCount.append("")

                    if postTypes[c] == "twitter":  # if the post type is Twitter it goes through more processing
                        tweetCount = tweetCount + 1  # counts number of tweets
                        tweetSplit = urls[c].split("statuses/")  # splits URL to get tweetID
                        tweetIDs[c] = tweetSplit[1]
                        tempTweetIDs.append(tweetIDs[c])

                        if tweetCount == 100:  # the max number of TweetIDs in one API call is 100 so a call is run every 100 tweets identified

                            tweepys = api.statuses_lookup(id_=tempTweetIDs)  # call to Twitter API

                            for tweet in tweepys:
                                tempID = tweet.id_str  # finds tweetsID
                                postMatch = 0

                                for idMatch in tweetIDs:
                                    if idMatch == tempID:  # matches tweetID in Twitter API call to tweetID stored from Crimson API
                                        tempDate = str(tweet.created_at).replace("  ",
                                                                                 " ")  # These all fill the matching Crimson attributes to those found in the Twitter API
                                        dateTime = tempDate.split(" ")
                                        postDates[postMatch] = dateTime[0]
                                        postTimes[postMatch] = dateTime[1]
                                        contents[postMatch] = tweet.text.replace(",", "")
                                        authors[postMatch] = tweet.author.screen_name
                                        followers[postMatch] = str(tweet.author.followers_count)
                                        friends[postMatch] = str(tweet.author.friends_count)
                                        retweetCounts[postMatch] = str(tweet.retweet_count)
                                        favoritesCount[postMatch] = str(tweet.favorite_count)
                                        statusesCount[postMatch] = str(tweet.author.statuses_count)

                                    postMatch = postMatch + 1

                            tweetCount = 0  # clears tweet count for a new 100
                            tempTweetIDs = []  # clears tweetIDs for next call

                    sentiments.append("")

                    neutralScore.append("")

                    positiveScore.append("")

                    negativeScore.append("")

                    if ('categoryScores' in i):  # finds sentiment value and matching attribute
                        for l in i["categoryScores"]:
                            catName = l["categoryName"]
                            if catName == "Basic Neutral":
                                neutralScore[c] = l["score"]
                            elif catName == "Basic Positive":
                                positiveScore[c] = l["score"]
                            elif catName == "Basic Negative":
                                negativeScore[c] = l["score"]

                    if neutralScore[c] > positiveScore[c] and neutralScore[c] > negativeScore[c]:
                        sentiments[c] = "Basic Neutral"

                    if positiveScore[c] > neutralScore[c] and positiveScore[c] > negativeScore[c]:
                        sentiments[c] = "Basic Positive"

                    if negativeScore[c] > positiveScore[c] and negativeScore[c] > neutralScore[c]:
                        sentiments[c] = "Basic Negative"

                    c = c + 1

                if len(
                        tempTweetIDs) != 0:  # after loop the Twitter API call must run one more time to clean up all the tweets since the last 100
                    try:
                        tweepys = api.statuses_lookup(id_=tempTweetIDs)

                        for tweet in tweepys:
                            tempID = tweet.id_str
                            postMatch = 0

                            for idMatch in tweetIDs:
                                if idMatch == tempID:
                                    tempDate = str(tweet.created_at).replace("  ", " ")
                                    dateTime = tempDate.split(" ")
                                    postDates[postMatch] = dateTime[0]
                                    postTimes[postMatch] = dateTime[1]
                                    contents[postMatch] = tweet.text.replace(",", "")
                                    authors[postMatch] = tweet.author.screen_name
                                    followers[postMatch] = str(tweet.author.followers_count)
                                    friends[postMatch] = str(tweet.author.friends_count)
                                    retweetCounts[postMatch] = str(tweet.retweet_count)
                                    favoritesCount[postMatch] = str(tweet.favorite_count)
                                    statusesCount[postMatch] = str(tweet.author.statuses_count)
                                postMatch = postMatch + 1
                        tweetCount = 0
                    except:
                        print("Tweepy error: skipping cleanup")

                pC = 0
                for pDate in postDates:  # iterates through the word lists and prints matching posts to CSV
                    csvRow = [postTypes[pC], pDate, postTimes[pC], urls[pC], str(tweetIDs[pC]),
                              contents[pC].replace("\n", " "), retweetCounts[pC], favoritesCount[pC], locations[pC],
                              languages[pC], sentiments[pC], str(neutralScore[pC]), str(positiveScore[pC]),
                              str(negativeScore[pC]), followers[pC], friends[pC], authors[pC], authorGenders[pC],
                              statusesCount[pC]]
                    writer.writerow(csvRow)
                    pC = pC + 1
            return fname
        else:
            raise ValueError("Server Error, No Data" + str(webURL.getcode()))


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'crimson')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    today = date.today()
    yesterday = today - timedelta(days=1)
    dayBeforeYesterday = today - timedelta(days=2)
    fname = collect_crimson_monitor_data(dayBeforeYesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d"),
                                         localPath)

    # s3.upload("macroscope-paho-covid", localPath, "input/crimson", fname)

    return None

if __name__ =="__main__":
    lambda_handler(None, None)