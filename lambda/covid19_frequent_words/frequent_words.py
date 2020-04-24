import os
from urllib.parse import unquote_plus

import nltk
from nltk import ngrams, word_tokenize
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer


import pandas as pd
import writeToS3 as s3
import plot

def lambda_handler(event, context):
    # create local path
    localPath = os.path.join('/tmp', 'frequent_words')
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
    hash = extract_frequent_words(df)

    # plot bar chart (frequency chart)
    index = hash['hashtags'].values.tolist()[:10]
    counts = hash['Freq'].values.tolist()[:10]
    title = 'Top 10 prevalent hashtags (' + filename.split(".")[0] +')'
    div = plot.plot_bar_chart(index, counts, title)

    # save result and write back to s3
    hash_filename = filename.split(".")[0]

    hash.to_csv(os.path.join(localPath, hash_filename + "_extracted_hashtag.csv"), index=False)
    s3.upload("macroscope-paho-covid", localPath, "frequent_words", hash_filename + "_extracted_hashtag.csv")

    with open(os.path.join(localPath, hash_filename + "_extracted_hashtag_frequency.html"), 'w') as f:
        f.write(div)
    s3.upload("macroscope-paho-covid", localPath, "frequent_words", hash_filename + "_extracted_hashtag_frequency.html")

    return None


def big_string(list_of_words):
    text = ""
    for i in list_of_words:
        text += str(i) + " "
    return text

def ngram(list_of_str,n):
    make_string = ' '.join(list_of_str)
    return ngrams(make_string.split(),n)

def tokenize_no_stop(string):
    lemmatizer = WordNetLemmatizer()

    word_tokens = word_tokenize(string)
    lower_tokens = [word.lower() for word in word_tokens if word.isalpha()]

    stopwords = nltk.corpus.stopwords.words("spanish") + nltk.corpus.stopwords.words(
        "english") + nltk.corpus.stopwords.words("portuguese") + ["rt", "http", "https"]

    tokens_no_stops = [word for word in lower_tokens if word not in stopwords]
    lemma_tokens = [lemmatizer.lemmatize(word) for word in tokens_no_stops]
    return lemma_tokens


def extract_frequent_words(df):
    hashtags = ["COVID19", "coronavirus", "COVID_19"]

    # filter df by hashtag
    for hashtag in hashtags:
        new_df = df[df['Contents'].str.contains("#" + hashtag, na=False)]

        most_common = FreqDist(tokenize_no_stop(big_string(new_df['Contents'].values))).most_common(10)
        most_common_bigrams = FreqDist(ngram(tokenize_no_stop(big_string(new_df['Contents'].values)), 2)).most_common(10)
        most_common_trigrams = FreqDist(ngram(tokenize_no_stop(big_string(new_df['Contents'].values)), 3)).most_common(10)

        # Plot and save

        # upload to s3

if __name__ == '__main__':
    df = pd.read_csv('test.csv')
    extract_frequent_words(df)




