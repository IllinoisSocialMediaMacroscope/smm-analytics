import json
import os
import urllib.request
from datetime import date, timedelta
from operator import itemgetter

import plot
import writeToS3 as s3


def getAuthToken():  # provides auth token needed to access Crimson API
    authToken = os.environ['crimsonAuthToken']
    authToken = "&auth=" + authToken
    return authToken


def crimson_sentiment(projectStartDate, projectEndDate, localPath):
    monitorID = os.environ['monitorID']
    urlStart = "https://api.crimsonhexagon.com/api"
    fnames = []

    dates = "&start=" + projectStartDate + "&end=" + projectEndDate  # Combines start and end date into format needed for API call
    authToken = getAuthToken()  # Gets auth token
    endpoint = "/monitor/results?id="  # endpoint needed for this query
    urlData = urlStart + endpoint + monitorID + authToken + dates  # Combines all API calls parts into full URL

    webURL = urllib.request.urlopen(urlData)

    if webURL.getcode() == 200:

        data = webURL.read().decode('utf8')
        theJSON = json.loads(data)

        # write json content
        fname = "monitorID_" + monitorID + "_extracted_results.json"
        with open(os.path.join(localPath, fname), 'w') as f:
            json.dump(theJSON, f, indent=2)

        fnames.append(fname)

        # plot pie charts and save to html
        results = theJSON["results"][0]

        labels = []
        values = []
        for metric in ["categories", "emotions"]:
            label = []
            value = []
            for item in results[metric]:
                label.append(item['category'])
                value.append(item['volume'])
            labels.append(label)
            values.append(value)

        subtitles = ["Basic Sentiment Categories", "Emotions"]
        div = plot.plot_multiple_pie_chart(labels, values, subtitles)
        div_fname = "monitorID_" + monitorID + "_extracted_results.html"
        with open(os.path.join(localPath, div_fname), 'w') as f:
            f.write(div)

        fnames.append(div_fname)

    else:
        raise ValueError("Server Error, No Data" + str(webURL.getcode()))

    return fnames


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'sentiment')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    # collect top sources and plot
    today = date.today()
    yesterday = today - timedelta(days=1)
    dayBeforeYesterday = today - timedelta(days=2)
    fnames = crimson_sentiment(dayBeforeYesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d"),
                                 localPath)
    for fname in fnames:
        s3.upload("macroscope-paho-covid", localPath, "sentiment", fname)

    return None


if __name__ == "__main__":
    lambda_handler(None, None)
