from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer, FreqDist, pos_tag_sents, PorterStemmer
import re
import os


class Preprocess:

    def __init__(self, df, column):

        sentences = df[df[column] != ''][column].dropna().astype(
            'str').tolist()
        sentences = [re.sub(r"http\S+", "", tweet) for tweet in sentences]
        self.sentences = sentences

    def get_phrases(self):
        phrases = []
        puncList = '.;,:!?/\\)(\"\''
        regex = re.compile('[%s%s]' % (puncList, '|\t\n'))
        for item in self.sentences:
            for i in regex.split(item):
                if i != '' and i.isdigit() == False and len(i) > 20:
                    phrases.append([i.lower()])
        phrases.insert(0, ['Phrase'])

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

        filtered_tokens = []
        for token in tokens:
            # third party stopwors:https://sites.google.com/site/kevinbouge/stopwords-lists
            # twitter specific stopwordshttps://sites.google.com/site/iamgongwei/home/sw
            # nltk stopwords
            filtered_tokens.append(
                [word.lower() for word in token if
                 (word.lower() not in stopwords.words('english'))
                 and (word.lower() not in stopwords2)
                 and (word.isalpha() == True or word[0] == '#' or word[
                     0] == '$')
                 and (word.lower() not in stopwords3)])

        return filtered_tokens

    def stem_lematize(self, process, filtered_tokens):
        processed_tokens = []
        if process == 'lemmatization':
            wnl = WordNetLemmatizer()
            for tk in filtered_tokens:
                processed_tokens.append([wnl.lemmatize(t) for t in tk])
        elif process == 'stemming':
            porter = PorterStemmer()
            for tk in filtered_tokens:
                processed_tokens.append([porter.stem(t) for t in tk])
        elif process == 'both':
            wnl = WordNetLemmatizer()
            porter = PorterStemmer()
            for tk in filtered_tokens:
                processed_tokens.append(
                    [wnl.lemmatize(porter.stem(t)) for t in tk])

        return processed_tokens

    def tagging(self, tagger, processed_tokens):
        tag = []
        if tagger == 'posTag':
            tag = pos_tag_sents(processed_tokens)

        return tag

    def most_frequent(self, filtered_tokens, processed_tokens):
        filtered_document = []
        for sent_token in filtered_tokens:
            filtered_document += sent_token
        processed_document = []
        for sent_token in processed_tokens:
            processed_document += sent_token

        filtered_most_common = FreqDist(filtered_document).most_common()
        filtered_most_common.insert(0, ['word','frequency'])
        processed_most_common = FreqDist(processed_document).most_common()
        processed_most_common.insert(0, ['word', 'frequency'])

        return filtered_most_common, processed_most_common
