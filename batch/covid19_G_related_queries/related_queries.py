import os

import pandas as pd
import plot
import writeToS3 as s3
from pytrends.request import TrendReq
import imgkit


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'related_queries')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    keywords = ['ventilador', 'ventiladores', 'mascarilla', 'mascarillas medicas', 'mascarillas de proteccion',
                'pantalla facial', 'tapabocas']
    related_queries(keywords, "spanish", localPath)

    return None


def related_queries(keywords, language, localPath):
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
            df_queries = pytrend.related_queries()

            for keyword in keywords_split:

                if keyword not in indices.keys():
                    indices[keyword] = []
                if keyword not in counts.keys():
                    counts[keyword] = []
                if keyword not in title.keys():
                    title[keyword] = []
                if keyword not in subtitles.keys():
                    subtitles[keyword] = []

                df_top = df_queries[keyword]['top']
                df_rising = df_queries[keyword]['rising']

                if df_top is not None and df_rising is not None:
                    # plot bar chart side by side
                    indices[keyword].append([df_top["query"].tolist()[:10], df_rising["query"].tolist()[:10]])
                    counts[keyword].append([df_top["value"].tolist()[:10], df_rising["value"].tolist()[:10]])
                    title[keyword] = "Google Trends Queries related to keyword: " + keyword
                    subtitles[keyword].append(["top related query(" + timeframes[timeframe] + ")",
                                               "rising related query(" + timeframes[timeframe] + ")"])

                    # save csv
                    df_top.rename(columns={'query': 'top related query'}, inplace=True)
                    df_rising.rename(columns={'query': 'rising related query'}, inplace=True)
                    result = pd.concat([df_top, df_rising], axis=1)
                    result.to_csv(os.path.join(localPath, keyword.replace(" ", "_") + "_" + timeframes[timeframe] +
                                               "_related_queries.csv"), index=False)
                    s3.upload("macroscope-paho-covid", localPath, "related_queries",
                              keyword.replace(" ", "_") + "_" + timeframes[timeframe] +
                              "_related_queries.csv")

        for keyword in keywords_split:
            if indices[keyword] != [] and counts[keyword] != [] and title[keyword] != [] and subtitles[keyword] != []:
                div = plot.plot_multiple_bar_chart(indices[keyword], counts[keyword], title[keyword],
                                                      subtitles[keyword])
                with open(os.path.join(localPath, keyword.replace(" ", "_") + "_related_queries.html"), 'w') as f:
                    f.write(div)
                s3.upload("macroscope-paho-covid", localPath, "related_queries",
                          keyword.replace(" ", "_") + "_related_queries.html")

                # static image
                imgkit.from_file(os.path.join(localPath, keyword.replace(" ", "_") + "_related_queries.html"),
                                 os.path.join(localPath, keyword.replace(" ", "_") + "_related_queries.png"),
                                 options={"xvfb": ""})
                s3.upload("macroscope-paho-covid", localPath, "related_queries",
                          keyword.replace(" ", "_") + "_related_queries.png")

    return None

if __name__ == "__main__":
    lambda_handler(None, None)