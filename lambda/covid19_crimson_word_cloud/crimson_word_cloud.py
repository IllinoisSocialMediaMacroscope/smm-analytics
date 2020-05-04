import json
import os
import urllib.request
from datetime import date, timedelta
from collections import OrderedDict
from operator import itemgetter

import writeToS3 as s3
import plot


def getAuthToken():  # provides auth token needed to access Crimson API
    authToken = os.environ['crimsonAuthToken']
    authToken = "&auth=" + authToken
    return authToken


def DatePull(startdate, enddate):
    listArray = []
    startdate = date(int(startdate[0:4]), int(startdate[5:7]), int(startdate[8:10]))
    enddate = date(int(enddate[0:4]), int(enddate[5:7]), int(enddate[8:10]))

    while startdate <= enddate:
        listArray.append(str(startdate))
        startdate += timedelta(days=1)
    return listArray


def crimson_word_cloud(projectStartDate, projectEndDate, localPath):
    monitorID = os.environ['monitorID']
    lineArray = DatePull(projectStartDate, projectEndDate)
    urlStart = "https://api.crimsonhexagon.com/api"
    fnames = []

    for i in range(len(lineArray) - 1):
        startDate = lineArray[i]
        endDate = lineArray[i + 1]

        dates = "&start=" + startDate + "&end=" + endDate  # Combines start and end date into format needed for API call
        authToken = getAuthToken()  # Gets auth token
        endpoint = "/monitor/wordcloud?id="  # endpoint needed for this query
        urlData = urlStart + endpoint + monitorID + authToken + dates  # Combines all API calls parts into full URL

        webURL = urllib.request.urlopen(urlData)

        if webURL.getcode() == 200:

            data = webURL.read().decode('utf8')
            theJSON = json.loads(data)["data"]
            sortedJSON = OrderedDict(sorted(theJSON.items(), key=itemgetter(1), reverse=True))

            # write json content
            fname = "Monitor-" + monitorID + '-wordcloud-from-' + startDate + '-to-' + endDate + '.json'
            with open(os.path.join(localPath, fname), 'w') as f:
                json.dump(sortedJSON, f, indent=2)

            fnames.append(fname)

            # plot word cloud and save to html
            div_fname = "Monitor-" + monitorID + '-wordcloud-from-' + startDate + '-to-' + endDate + '.html'
            div = plot.word_cloud(list(sortedJSON.keys()), list(sortedJSON.values()))
            with open(os.path.join(localPath, div_fname), 'w') as f:
                f.write(div)

            fnames.append(div_fname)

        else:
            raise ValueError("Server Error, No Data" + str(webURL.getcode()))

    return fnames


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'wordcloud')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    # collect word cloud and plot
    today = date.today()
    yesterday = today - timedelta(days=1)
    dayBeforeYesterday = today - timedelta(days=2)
    fnames = crimson_word_cloud(dayBeforeYesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d"),
                               localPath)
    for fname in fnames:
        s3.upload("macroscope-paho-covid", localPath, "wordcloud", fname)

    return None
