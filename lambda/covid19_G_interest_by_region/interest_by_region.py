import os

import pandas as pd
import plot
import writeToS3 as s3
from pytrends.request import TrendReq


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'interest_by_region')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    keywords = ['ventilador', 'ventiladores', 'mascarilla', 'mascarillas medicas', 'mascarillas de proteccion',
                'pantalla facial', 'tapabocas']
    interest_by_region(keywords, "spanish", localPath)

    return None


def interest_by_region(keywords, language, localPath):
    country_code = pd.read_csv("tableconvert_csv_j8hnfj.csv", quotechar = "\"")
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

        pytrend.build_payload(kw_list=keywords_split)
        df_regions = pytrend.interest_by_region(inc_geo_code=True)
        df_regions['country'] = df_regions.index
        df_regions = pd.merge(df_regions, country_code, left_on="geoCode", right_on="Alpha-2 code", how="left")

        for keyword in keywords_split:
            geo_name_df = df_regions[['country', keyword, 'Alpha-2 code', 'Alpha-3 code', 'Numeric code',
                                      'Latitude (average)', 'Longitude (average)']]

            if geo_name_df is not None:
                title = "Google Trends Interest by Region related to keyword: " + keyword
                div = plot.plot_geograph(geo_name_df, keyword, title)
                with open(os.path.join(localPath, keyword.replace(" ", "_") + "_interest_by_region.html"), 'w') as f:
                    f.write(div)
                s3.upload("macroscope-paho-covid", localPath, "interest_by_region",
                          keyword.replace(" ", "_") + "_interest_by_region.html")

                # save csv
                geo_name_df.to_csv(os.path.join(localPath, keyword.replace(" ", "_") + "_interest_by_region.csv"),
                                   index=False)
                s3.upload("macroscope-paho-covid", localPath, "interest_by_region",
                          keyword.replace(" ", "_") + "_interest_by_region.csv")


    return None


if __name__ == "__main__":
    lambda_handler(None, None)