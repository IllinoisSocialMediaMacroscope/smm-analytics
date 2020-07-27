import csv
import os

import imgkit
import plot
import writeToS3 as s3
from pytrends.request import TrendReq


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'keyword_suggestions')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    keywords = ['ventilador', 'ventiladores', 'mascarilla', 'mascarillas medicas', 'mascarillas de proteccion',
                'pantalla facial', 'tapabocas']
    keyword_suggestions(keywords, "spanish", localPath)

    return None


def keyword_suggestions(keywords, language, localPath):
    if language.lower() == 'spanish':
        pytrend = TrendReq(hl='sp-SP')
    else:
        pytrend = TrendReq()

    for keyword in keywords:
        suggestions = pytrend.suggestions(keyword)
        if len(suggestions) > 0:
            # save csv
            with open(os.path.join(localPath, keyword.replace(" ", "_") + "_keyword_suggestions.csv"), "w",
                      encoding="utf-8") as f:
                dict_writer = csv.DictWriter(f, suggestions[0].keys())
                dict_writer.writeheader()
                dict_writer.writerows(suggestions)

            s3.upload("macroscope-paho-covid", localPath, "keyword_suggestions",
                      keyword.replace(" ", "_") + "_keyword_suggestions.csv")

            # plot table
            header = list(suggestions[0].keys())
            cell = []
            for k in header:
                row = []
                for s in suggestions:
                    row.append(s[k])
                cell.append(row)
            div = plot.plot_table("keyword suggestions for: " + keyword, header, cell)
            with open(os.path.join(localPath, keyword.replace(" ", "_") + "_keyword_suggestions.html"), 'w') as f:
                f.write(div)
            s3.upload("macroscope-paho-covid", localPath, "keyword_suggestions",
                      keyword.replace(" ", "_") + "_keyword_suggestions.html")

            # static image
            imgkit.from_file(os.path.join(localPath, keyword.replace(" ", "_") + "_keyword_suggestions.html"),
                             os.path.join(localPath, keyword.replace(" ", "_") + "_keyword_suggestions.png"),
                             options={"xvfb": ""})
            s3.upload("macroscope-paho-covid", localPath, "keyword_suggestions",
                      keyword.replace(" ", "_") + "_keyword_suggestions.png")

    return None


if __name__ == "__main__":
    lambda_handler(None, None)
