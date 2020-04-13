import os
from urllib.parse import unquote_plus

import pandas as pd
import writeToS3 as s3


def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'hashtag')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    # download triggered file
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    remotePath = "/".join(key.split("/")[:-1])
    filename = key.split("/")[-1]
    s3.downloadToDisk(bucket, filename, localPath, remotePath)

    # load to dataframe
    df = pd.read_csv(os.path.join(localPath, filename))

    # extract hashtag
    hash = extract_hashtag(df)

    # save result and write back to s3
    hash_filename = filename + "_extracted_hashtag.csv"
    hash.to_csv(os.path.join(localPath, hash_filename), index=False)
    s3.upload("macroscope-paho-covid", localPath, "", hash_filename)

    return None


def extract_hashtag(df):
    df["hashtags"] = df.Contents.str.findall(r"#(\w+)")
    hash = df['hashtags'].apply(pd.Series)
    hash = hash.stack().value_counts()
    hash.index = "#" + hash.index.astype(str)

    hash = hash.to_frame(name='Freq')
    hash['hashtags'] = hash.index
    hash = hash.reset_index(drop=True)
    hash['pubshare'] = hash['Freq'] / (hash['Freq'].sum())

    return hash
