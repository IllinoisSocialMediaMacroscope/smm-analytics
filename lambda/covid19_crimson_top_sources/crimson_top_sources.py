import json
import os
import urllib.request
from datetime import date, timedelta

import plot
import writeToS3 as s3


def getAuthToken():  # provides auth token needed to access Crimson API
    authToken = os.environ['brandwatchAuthToken']
    authToken = "&access_token=" + authToken
    return authToken


def crimson_top_sources(projectStartDate, projectEndDate, localPath):
    monitorID = os.environ['monitorID']
    urlStart = "https://api.brandwatch.com"

    dates = "&startDate=" + projectStartDate + "&endDate=" + projectEndDate   # Combines start and end date into format needed for API call
    authToken = getAuthToken()  # Gets auth token
    topsite_endpoint = "/projects/1998292854/data/volume/topsites/queries?"  # endpoint needed for this query
    toptweeter_endpoint = "/projects/1998292854/data/volume/toptweeters/queries?"
    urlData = {
        "top_sites":  urlStart + topsite_endpoint + 'queryId=' + monitorID + authToken + dates,
        "top_tweeters": urlStart + toptweeter_endpoint + 'queryId=' + monitorID + authToken + dates
    }

    fnames = []
    labels = []
    values = []
    subtitles = []
    for metric in urlData.keys():
        webURL = urllib.request.urlopen(urlData[metric])

        if webURL.getcode() == 200:

            data = webURL.read().decode('utf8')
            theJSON = json.loads(data)

            # write json content
            fname = "monitorID_" + monitorID + "_extracted_" + metric + ".json"
            with open(os.path.join(localPath, fname), 'w') as f:
                json.dump(theJSON, f, indent=2)

            fnames.append(fname)

            # plot bar charts and save to html
            sources = theJSON["results"]
            label = []
            value = []
            for source in sources:
                label.append(source['name'])
                value.append(source['data']['volume'])

            subtitles.append(metric)
            labels.append(label)
            values.append(value)
        else:
            raise ValueError("Server Error, No Data" + str(webURL.getcode()))

    div, image = plot.plot_multiple_pie_chart(labels, values, subtitles)
    div_fname = "monitorID_" + monitorID + "_extracted_top_sources.html"
    with open(os.path.join(localPath, div_fname), 'w') as f:
        f.write(div)

    fnames.append(div_fname)

    png_fname = "monitorID_" + monitorID + "_extracted_top_sources.png"
    image.save(os.path.join(localPath, png_fname))
    fnames.append(png_fname)

    return fnames


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'top_sources')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    # collect top sources and plot
    today = date.today()
    yesterday = today - timedelta(days=1)
    dayBeforeYesterday = today - timedelta(days=2)
    fnames = crimson_top_sources(dayBeforeYesterday.strftime("%Y-%m-%d"), yesterday.strftime("%Y-%m-%d"),
                                 localPath)
    for fname in fnames:
        s3.upload("macroscope-paho-covid", localPath, "top_sources", fname)

    return None


if __name__ == "__main__":
    lambda_handler(None, None)
