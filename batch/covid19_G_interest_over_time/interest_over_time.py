import os

import imgkit
import plot
import writeToS3 as s3
from pytrends.request import TrendReq


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'interest_over_time')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    keywords = ['ventilador', 'ventiladores', 'mascarilla', 'mascarillas medicas', 'mascarillas de proteccion',
                'pantalla facial', 'tapabocas']
    interest_over_time(keywords, "spanish", localPath)

    return None


def interest_over_time(keywords, language, localPath):
    if language.lower() == 'spanish':
        pytrend = TrendReq(hl='sp-SP')
    else:
        pytrend = TrendReq()

    timeframes = {'now 1-d': '1day', 'now 7-d': '7days', 'today 1-m': '30days'}

    # there is a limit on 100 characters for keywords break them to multiple requests then
    while len(keywords) > 0:
        character_len = 0
        keywords_split = []
        for kk in keywords:
            character_len += len(kk)
            if character_len < 50:
                keywords_split.append(kk)
        for item in keywords_split:
            keywords.remove(item)

        indices = {}
        counts = {}
        title = {}
        subtitles = {}

        for timeframe in timeframes.keys():
            pytrend.build_payload(kw_list=keywords_split, timeframe=timeframe)
            df_interest = pytrend.interest_over_time()

            for keyword in keywords_split:

                if keyword not in indices.keys():
                    indices[keyword] = []
                if keyword not in counts.keys():
                    counts[keyword] = []
                if keyword not in title.keys():
                    title[keyword] = []
                if keyword not in subtitles.keys():
                    subtitles[keyword] = []

                indices[keyword].append([df_interest[keyword].index.tolist()])
                counts[keyword].append([df_interest[keyword].tolist()])
                title[keyword] = "Google Trends Interest over Time related to keyword: " + keyword
                subtitles[keyword].append(["Interest Over Time(" + timeframes[timeframe] + ")"])

                # save csv
                df_interest[keyword].to_csv(os.path.join(localPath, keyword.replace(" ", "_")
                                                         + "_" + timeframes[timeframe] + "_interest_over_time.csv"))

                s3.upload("macroscope-paho-covid", localPath, "interest_over_time",
                          keyword.replace(" ", "_") + "_" + timeframes[timeframe] +
                          "_interest_over_time.csv")

        for keyword in keywords_split:
            if indices[keyword] != [] and counts[keyword] != [] and title[keyword] != [] and subtitles[keyword] != []:
                div = plot.plot_multiple_time_series(indices[keyword], counts[keyword], title[keyword],
                                                     subtitles[keyword])
                with open(os.path.join(localPath, keyword.replace(" ", "_") + "_interest_over_time.html"), 'w') as f:
                    f.write(div)
                s3.upload("macroscope-paho-covid", localPath, "interest_over_time",
                          keyword.replace(" ", "_") + "_interest_over_time.html")

                # static image
                imgkit.from_file(os.path.join(localPath, keyword.replace(" ", "_") + "_interest_over_time.html"),
                                 os.path.join(localPath, keyword.replace(" ", "_") + "_interest_over_time.png"),
                                 options={"xvfb": ""})
                s3.upload("macroscope-paho-covid", localPath, "interest_over_time",
                          keyword.replace(" ", "_") + "_interest_over_time.png")

    return None

if __name__ == "__main__":
    lambda_handler(None, None)