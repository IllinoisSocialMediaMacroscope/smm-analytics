import pandas as pd
import os
from pytrends.request import TrendReq

def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'related_queries')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    keywords = ['ventilador', 'ventiladores', 'mascarilla', 'mascarillas médicas']
    df = related_queries(keywords, "spanish")


def related_queries(keywords, language):
    if language.lower() == 'spanish':
        pytrend = TrendReq(hl='sp-SP')
    else:
        pytrend = TrendReq()

    pytrend.build_payload(kw_list=keywords, timeframe='now 1-d')
    df_queries = pytrend.related_queries()

    for keyword in keywords:
        df_top = df_queries[keyword]['top']
        df_top.rename(columns={'query':'top related query'}, inplace=True)

        df_rising = df_queries[keyword]['rising']
        df_top.rename(columns={'query': 'rising related query'}, inplace=True)

        result = pd.concat([df_top, df_rising], axis=1)

        # save result
        # plot two bar chart side by side

    return df_queries

if __name__ == "__main__":
    keywords = ['ventilador', 'ventiladores', 'mascarilla', 'mascarillas médicas']
    df = related_queries(keywords, "spanish")