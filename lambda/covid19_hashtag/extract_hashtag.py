import os
from urllib.parse import unquote_plus

import pandas as pd
import writeToS3 as s3
import plot


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

    # plot bar chart (frequency chart)
    index = hash['hashtags'].values.tolist()[:10]
    counts = hash['Freq'].values.tolist()[:10]
    title = 'Top 10 prevalent hashtags (' + filename.split(".")[0] +')'
    div = plot.plot_bar_chart(index, counts, title)

    # save result and write back to s3
    hash_filename = filename.split(".")[0]

    hash.to_csv(os.path.join(localPath, hash_filename + "_extracted_hashtag.csv"), index=False)
    s3.upload("macroscope-paho-covid", localPath, "hashtags", hash_filename + "_extracted_hashtag.csv")

    with open(os.path.join(localPath, hash_filename + "_extracted_hashtag_frequency.html"), 'w') as f:
        f.write(div)
    s3.upload("macroscope-paho-covid", localPath, "hashtags", hash_filename + "_extracted_hashtag_frequency.html")

    return None


def extract_hashtag(df):
    if 'Contents' in df.columns:
        df["hashtags"] = df.Contents.str.findall(r"#(\w+)")
    elif 'full_text' in df.columns:
        df["hashtags"] = df['full_text'].str.findall(r"#(\w+)")
    elif 'text' in df.columns:
        df["hashtags"] = df['text'].str.findall(r"#(\w+)")
    else:
        raise ValueError("Unable to extract hashtag from this data source!")

    hash = df['hashtags'].apply(pd.Series)
    hash = hash.stack().value_counts()
    hash.index = "#" + hash.index.astype(str)

    hash = hash.to_frame(name='Freq')
    hash['hashtags'] = hash.index
    hash = hash.reset_index(drop=True)
    hash['pubshare'] = hash['Freq'] / (hash['Freq'].sum())

    return hash
