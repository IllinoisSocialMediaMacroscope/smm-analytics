import csv
import os

import nltk
import pandas as pd
import plot
import writeToS3 as s3
from nltk import ngrams, word_tokenize
from nltk.probability import FreqDist
from nltk.stem import WordNetLemmatizer


def lambda_handler():
    # create local path
    localPath = os.path.join('/tmp', 'frequent_phrases')
    if not os.path.exists(localPath):
        os.makedirs(localPath)

    # download triggered file
    bucket = "macroscope-paho-covid"
    remotePath = "input/brandwatch"
    files = s3.listFiles(bucket, remotePath)
    sorted_files = sorted(files, key=lambda file: file['LastModified'], reverse=True)

    hashtags = ["COVID19", "coronavirus", "COVID_19"]
    date_markers = ["1day", "7days", "30days"]

    for hashtag in hashtags:
        indices_row = []
        counts_row = []
        legends_row = []
        for date_marker in date_markers:
            if date_marker == "1day":
                today = sorted_files[0]['Key'].split("/")[-1]
                s3.downloadToDisk(bucket, today, localPath, remotePath)
                df_today = pd.read_csv(os.path.join(localPath, today))
                indices, counts = extract_frequent_phrases(df_today, hashtag, date_marker, localPath)
                legends = ["word (1day)", "bigram (1day)", "trigram(1day)"]
            elif date_marker == "7days":
                last_7_days_files = sorted_files[:7]
                last_7_days_list = []
                for file in last_7_days_files:
                    fname = file['Key'].split("/")[-1]
                    s3.downloadToDisk(bucket, fname, localPath, remotePath)
                    last_7_days_list.append(pd.read_csv(os.path.join(localPath, fname)))
                last_7_days_df = pd.concat(last_7_days_list, axis=0, ignore_index=True)
                indices, counts = extract_frequent_phrases(last_7_days_df, hashtag, date_marker, localPath)
                legends = ["word (7days)", "bigram (7days)", "trigram(7days)"]
            elif date_marker == "30days":
                last_30_days_files = sorted_files[:30]
                last_30_days_list = []
                for file in last_30_days_files:
                    fname = file['Key'].split("/")[-1]
                    s3.downloadToDisk(bucket, fname, localPath, remotePath)
                    last_30_days_list.append(pd.read_csv(os.path.join(localPath, fname)))
                last_30_days_list = pd.concat(last_30_days_list, axis=0, ignore_index=True)
                indices, counts = extract_frequent_phrases(last_30_days_list, hashtag, date_marker, localPath)
                legends = ["word (30days)", "bigram (30days)", "trigram(30days)"]
            else:
                break

            indices_row.append(indices)
            counts_row.append(counts)
            legends_row.append(legends)

        # Plot and save
        title = "Most prevalent 10 frequent words and phrases used in #" + hashtag + " tweets"
        div, image = plot.plot_multiple_bar_chart(indices_row, counts_row, title, legends_row)
        with open(os.path.join(localPath, hashtag + "_extracted_frequent_phrases.html"), 'w') as f:
            f.write(div)
        s3.upload("macroscope-paho-covid", localPath, "frequent_phrases", hashtag + "_extracted_frequent_phrases.html")

        image.save(os.path.join(localPath, hashtag + "_extracted_frequent_phrases.png"))
        s3.upload("macroscope-paho-covid", localPath, "frequent_phrases", hashtag + "_extracted_frequent_phrases.png")

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


def extract_frequent_phrases(df, hashtag, date_marker, localPath):
    # filter df by hashtag
    new_df = df[df['Contents'].str.contains("#" + hashtag, na=False)]

    most_common = FreqDist(tokenize_no_stop(big_string(new_df['Contents'].values)))
    most_common_bigrams = FreqDist(ngram(tokenize_no_stop(big_string(new_df['Contents'].values)), 2))
    most_common_trigrams = FreqDist(ngram(tokenize_no_stop(big_string(new_df['Contents'].values)), 3))

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

    # upload to s3
    with open(os.path.join(localPath, hashtag + "_" + date_marker + "_extracted_frequent_words.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(['word', 'count'])
        for row in most_common.most_common():
            writer.writerow(row)
    s3.upload("macroscope-paho-covid", localPath, "frequent_phrases", hashtag + "_" + date_marker + "_extracted_frequent_words.csv")

    with open(os.path.join(localPath, hashtag + "_" + date_marker + "_extracted_frequent_bigrams.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(['bigram', 'count'])
        for row in most_common_bigrams.most_common():
            writer.writerow(row)
    s3.upload("macroscope-paho-covid", localPath, "frequent_phrases", hashtag + "_" + date_marker + "_extracted_frequent_bigrams.csv")

    with open(os.path.join(localPath, hashtag + "_" + date_marker + "_extracted_frequent_trigrams.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(['trigram', 'count'])
        for row in most_common_trigrams.most_common():
            writer.writerow(row)
    s3.upload("macroscope-paho-covid", localPath, "frequent_phrases", hashtag + "_" + date_marker + "_extracted_frequent_trigrams.csv")

    return indices, counts
