import pandas as pd
import os
from pytrends.request import TrendReq
import plot
import writeToS3 as s3


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'related_queries')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    keywords = ['ventilador', 'ventiladores', 'mascarilla', 'mascarillas medicas',
                'mascarillas de proteccion', 'pantalla facial', 'tapabocas']
    related_queries(keywords, "spanish", localPath)

    return None


def related_queries(keywords, language, localPath):
    if language.lower() == 'spanish':
        pytrend = TrendReq(hl='sp-SP')
    else:
        pytrend = TrendReq()

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

        pytrend.build_payload(kw_list=keywords_split, timeframe='now 1-d')
        df_queries = pytrend.related_queries()

        for keyword in keywords_split:
            df_top = df_queries[keyword]['top']
            df_rising = df_queries[keyword]['rising']

            if df_top is not None and df_rising is not None:
                # plot bar chart side by side
                indices = [[df_top["query"].tolist()[:10], df_rising["query"].tolist()[:10]]]
                counts = [[df_top["value"].tolist()[:10], df_rising["value"].tolist()[:10]]]
                title = "Google Trends Queries related to keyword: " + keyword
                subtitles = [["top related query", "rising related query"]]
                div = plot.plot_multiple_bar_chart(indices, counts, title, subtitles)
                with open(os.path.join(localPath, keyword.replace(" ", "_") + "_related_queries.html"), 'w') as f:
                    f.write(div)
                s3.upload("macroscope-paho-covid", localPath, "related_queries", keyword.replace(" ", "_") + "_related_queries.html")

                # save csv
                df_top.rename(columns={'query': 'top related query'}, inplace=True)
                df_rising.rename(columns={'query': 'rising related query'}, inplace=True)
                result = pd.concat([df_top, df_rising], axis=1)
                result.to_csv(os.path.join(localPath, keyword.replace(" ", "_") + "_related_queries.csv"), index=False)
                s3.upload("macroscope-paho-covid", localPath, "related_queries", keyword.replace(" ", "_") + "_related_queries.csv")

    return None

if __name__ == "__main__":
    lambda_handler({}, None)