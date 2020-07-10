# work around to solve the issue that aws doesn't have sqlite compiled
import imp
import itertools
import sys

sys.modules["sqlite"] = imp.new_module("sqlite")
sys.modules["sqlite3.dbapi2"] = imp.new_module("sqlite.dbapi2")

import nltk

nltk.data.path.append('./nltk_data/')
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer, FreqDist, pos_tag, PorterStemmer
import re
import os


class Preprocess:

    def __init__(self, df, column):

        self.id_column = "id"
        if 'id_str' in df.columns:
            self.id_column = 'id_str'
            df_new = df[df[column] != ''][[self.id_column, column]].dropna()
            sentences = df_new[column].astype('str').tolist()
            self.id = df_new[self.id_column].astype('str').tolist()
        elif 'id' in df.columns:
            self.id_column = 'id'
            df_new = df[df[column] != ''][[self.id_column, column]].dropna()
            sentences = df_new[column].astype('str').tolist()
            self.id = df_new[self.id_column].astype('str').tolist()
        elif 'comment_id' in df.columns:
            self.id_column = 'comment_id'
            df_new = df[df[column] != ''][[self.id_column, column]].dropna()
            sentences = df_new[column].astype('str').tolist()
            self.id = df_new[self.id_column].astype('str').tolist()
        elif '_source.id_str':
            self.id_column = '_source.id_str'
            df_new = df[df[column] != ''][[self.id_column, column]].dropna()
            sentences = df_new[column].astype('str').tolist()
            self.id = df_new[self.id_column].astype('str').tolist()
        elif '_source.id':
            self.id_column = '_source.id_str'
            df_new = df[df[column] != ''][[self.id_column, column]].dropna()
            sentences = df_new[column].astype('str').tolist()
            self.id = df_new[self.id_column].astype('str').tolist()
        else:
            sentences = df[df[column] != ''][column].dropna().astype(
                'str').tolist()
            self.id = []

        sentences = [re.sub(r"http\S+", "", tweet) for tweet in sentences]
        self.sentences = sentences

    def get_phrases(self):
        phrases = [[self.id_column, 'Phrase']]
        puncList = '.;,:!?/\\)(\"\''
        regex = re.compile('[%s%s]' % (puncList, '|\t\n'))
        for sent_id, sent in itertools.zip_longest(self.id, self.sentences):
            for phrase in regex.split(sent):
                if phrase != '' and phrase.isdigit() == False and len(
                        phrase) > 20:
                    phrases.append([sent_id, phrase.lower()])

        return phrases

    def get_words(self):
        tknz = TweetTokenizer()
        tokens = [tknz.tokenize(t) for t in self.sentences]

        # nltk's stopwords are too weak
        with open(os.path.dirname(__file__) + '/stopwords_en.txt', 'r') as f:
            stopwords2 = f.read().split('\n')
        with open(os.path.dirname(__file__) + '/twitter-customized.txt',
                  'r') as f:
            stopwords3 = f.read().split(',')

        filtered_tokens = [[self.id_column, 'Filtered Word']]
        for sent_id, token in itertools.zip_longest(self.id, tokens):
            # third party stopwors:https://sites.google.com/site/kevinbouge/stopwords-lists
            # twitter specific stopwordshttps://sites.google.com/site/iamgongwei/home/sw
            # nltk stopwords
            temp = [sent_id]
            for word in token:
                if word.lower() not in stopwords.words('english') \
                        and word.lower() not in stopwords2 \
                        and (word.isalpha() == True or word[0] == '#' or word[0] == '$') \
                        and word.lower() not in stopwords3:
                    temp.append(word)
            filtered_tokens.append(temp)

        return filtered_tokens

    def stem_lematize(self, process, filtered_tokens, header=True):
        if header:
            filtered_tokens = filtered_tokens[1:]
        processed_tokens = []
        if process == 'lemmatization':
            processed_tokens.append([self.id_column, 'lemmatization'])
            wnl = WordNetLemmatizer()
            for tk in filtered_tokens:
                processed_tokens.append([wnl.lemmatize(t) for t in tk])
        elif process == 'stemming':
            processed_tokens.append([self.id_column, 'stemming'])
            porter = PorterStemmer()
            for tk in filtered_tokens:
                processed_tokens.append([porter.stem(t) for t in tk])
        elif process == 'both':
            processed_tokens.append([self.id_column, 'lemmatization+stemming'])
            wnl = WordNetLemmatizer()
            porter = PorterStemmer()
            for tk in filtered_tokens:
                processed_tokens.append(
                        [wnl.lemmatize(porter.stem(t)) for t in tk])

        return processed_tokens

    def tagging(self, tagger, processed_tokens):
        tag = [[self.id_column, "POS tags"]]
        for sent_id, sent_token in itertools.zip_longest(self.id, processed_tokens):
            if tagger == 'posTag':
                # don't add id if exist:
                    if len(self.id) > 0:
                        tag.append([sent_id] + pos_tag(sent_token[1:]))
                    else:
                        tag.append([None] + pos_tag(sent_token))

        return tag

    def most_frequent(self, filtered_tokens, processed_tokens, header=True):
        if header:
            filtered_tokens = filtered_tokens[1:]
            processed_tokens = processed_tokens[1:]

        filtered_document = []
        for sent_token in filtered_tokens:
            # don't add id to the total document
            if len(self.id) > 0:
                filtered_document += sent_token[1:]
            else:
                filtered_document += sent_token

        processed_document = []
        for sent_token in processed_tokens:
            if len(self.id) > 0:
                processed_document += sent_token[1:]
            else:
                filtered_document += sent_token

        filtered_most_common = FreqDist(filtered_document).most_common()
        filtered_most_common.insert(0, ['word', 'frequency'])
        processed_most_common = FreqDist(processed_document).most_common()
        processed_most_common.insert(0, ['word', 'frequency'])

        return filtered_most_common, processed_most_common
