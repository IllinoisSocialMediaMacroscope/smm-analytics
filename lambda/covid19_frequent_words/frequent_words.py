import csv
import os
from urllib.parse import unquote_plus

import nltk
import pandas as pd
import plot
import writeToS3 as s3
from nltk import ngrams, word_tokenize
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer


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
    extract_frequent_words(df, localPath)

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


def extract_frequent_words(df, localPath):
    hashtags = ["COVID19", "coronavirus", "COVID_19"]

    # filter df by hashtag
    for hashtag in hashtags:
        new_df = df[df['Contents'].str.contains("#" + hashtag, na=False)]

        most_common = FreqDist(tokenize_no_stop(big_string(new_df['Contents'].values)))
        most_common_bigrams = FreqDist(ngram(tokenize_no_stop(big_string(new_df['Contents'].values)), 2))
        most_common_trigrams = FreqDist(ngram(tokenize_no_stop(big_string(new_df['Contents'].values)), 3))

        # Plot and save
        title = "Most prevalent 10 frequent words and phrases used in #" + hashtag + " tweets"
        subtitles = ["words", "bigrams", "trigrams"]

        indices = []
        counts = []
        for phrases in [most_common.most_common(10),
                        most_common_bigrams.most_common(10),
                        most_common_trigrams.most_common(10)]:
            index = []
            count = []
            for item in phrases:
                if isinstance(item[0], tuple):
                    index.append(' '.join(item[0]))
                else:
                    index.append(item[0])
                count.append(item[1])

            indices.append(index)
            counts.append(count)

        div = plot.plot_multiple_bar_chart(indices, counts, title, subtitles)

        # upload to s3
        with open(os.path.join(localPath, hashtag + "_extracted_frequent_words.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(['word', 'count'])
            for row in most_common.most_common():
                writer.writerow(row)
        s3.upload("macroscope-paho-covid", localPath, "frequent_phrases", hashtag + "_extracted_frequent_words.csv")

        with open(os.path.join(localPath, hashtag + "_extracted_frequent_bigrams.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(['bigram', 'count'])
            for row in most_common_bigrams.most_common():
                writer.writerow(row)
        s3.upload("macroscope-paho-covid", localPath, "frequent_phrases", hashtag + "_extracted_frequent_bigrams.csv")

        with open(os.path.join(localPath, hashtag + "_extracted_frequent_trigrams.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(['trigram', 'count'])
            for row in most_common_trigrams.most_common():
                writer.writerow(row)
        s3.upload("macroscope-paho-covid", localPath, "frequent_phrases", hashtag + "_extracted_frequent_trigrams.csv")

        with open(os.path.join(localPath, hashtag + "_extracted_frequent_phrases.html"), 'w') as f:
            f.write(div)
        s3.upload("macroscope-paho-covid", localPath, "frequent_phrases", hashtag + "_extracted_frequent_phrases.html")
