import os
from urllib.parse import unquote_plus

import nltk

if not os.path.exists('/tmp/nltk_data'):
    os.makedirs('/tmp/nltk_data')
nltk.download('punkt', download_dir='/tmp/nltk_data')
nltk.download('stopwords', download_dir='/tmp/nltk_data')
nltk.data.path.append('/tmp/nltk_data/')

from nltk import word_tokenize
from nltk.probability import FreqDist

import pandas as pd
import json
import plot
import writeToS3 as s3


def big_string(list_of_words):
    text = ""
    for i in list_of_words:
        text += str(i) + " "
    return text


def tokenize_no_stop(string):
    word_tokens = word_tokenize(string)
    lower_tokens = [word.lower() for word in word_tokens if word.isalpha()]

    stopwords = nltk.corpus.stopwords.words("spanish") + nltk.corpus.stopwords.words(
        "english") + nltk.corpus.stopwords.words("portuguese") + ["rt", "http", "https", "nan"]

    tokens_no_stops = [word for word in lower_tokens if word not in stopwords]
    return tokens_no_stops


def word_cloud(df, localPath):
    monitorID = os.environ['monitorID']
    fnames = []

    # write json content
    fname = "monitorID_" + monitorID + "_extracted_wordcloud.json"
    wordcloud = {}

    most_common = FreqDist(tokenize_no_stop(big_string(df.values)))
    for item in most_common.most_common(100):
        if isinstance(item[0], tuple):
            wordcloud[' '.join(item[0])] = item[1]
        else:
            wordcloud[item[0]] = item[1]

    with open(os.path.join(localPath, fname), 'w') as f:
        json.dump(wordcloud, f, indent=2)

    fnames.append(fname)

    # plot word cloud and save to html
    div_fname = "monitorID_" + monitorID + "_extracted_wordcloud.html"
    div = plot.word_cloud(list(wordcloud.keys()), list(wordcloud.values()))
    with open(os.path.join(localPath, div_fname), 'w') as f:
        f.write(div)

    fnames.append(div_fname)

    return fnames


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'wordcloud')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    # download triggered file
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    remotePath = "/".join(key.split("/")[:-1])
    today = key.split("/")[-1]
    s3.downloadToDisk(bucket, today, localPath, remotePath)
    df_today = pd.read_csv(os.path.join(localPath, today))

    fnames = word_cloud(df_today, localPath)
    for fname in fnames:
        s3.upload("macroscope-paho-covid", localPath, "wordcloud", fname)

    return None


if __name__ == "__main__":
    event = {
        "Records": [
            {
                "eventVersion": "2.0",
                "eventSource": "aws:s3",
                "awsRegion": "us-west-2",
                "eventTime": "1970-01-01T00:00:00.000Z",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "EXAMPLE"
                },
                "requestParameters": {
                    "sourceIPAddress": "127.0.0.1"
                },
                "responseElements": {
                    "x-amz-request-id": "EXAMPLE123456789",
                    "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
                },
                "s3": {
                    "s3SchemaVersion": "1.0",
                    "configurationId": "testConfigRule",
                    "bucket": {
                        "name": "macroscope-paho-covid",
                        "ownerIdentity": {
                            "principalId": "EXAMPLE"
                        },
                        "arn": "arn:aws:s3:::example-bucket"
                    },
                    "object": {
                        "key": "input/crimson/Monitor-2000229793-from-2020-06-22-to-2020-06-23.csv",
                        "size": 1024,
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901"
                    }
                }
            }
        ]
    }
    lambda_handler(event, context=None)
