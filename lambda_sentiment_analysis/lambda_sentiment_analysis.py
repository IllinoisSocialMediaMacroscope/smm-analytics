import csv
import imp
import json
import os
import sys

# work around to solve the issue that aws lambda doesn't have sqlite compiled
sys.modules['sqlite'] = imp.new_module('sqlite')
sys.modules['sqlite3.dbapi2'] = imp.new_module('sqlite.dbapi2')

# add local path that holds nltk data into search path
import nltk
nltk.data.path.append('./nltk_data/')
from nltk import pos_tag, WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer, allcap_differential, negated
from nltk.tokenize import word_tokenize
from nltk.corpus import sentiwordnet as swn, stopwords
import plotly.graph_objs as go
from plotly.offline import plot
import pandas as pd

# custom helper functions to interact with aws s3 bucket
import writeToS3 as s3


class Sentiment:

    def __init__(self, awsPath, localSavePath, localReadPath, remoteReadPath, column):

        # private attributes
        __documentSentiment_flag = False

        # set paths:
        # localReadPath holds the temp input social media data
        # localSavePath holds temp outputs before uploading
        # awsPath is the s3 path to save
        self.localSavePath = localSavePath
        self.awsPath = awsPath

        # download remote socialmedia data (csv) into a temp folder
        # load csv to a pandas dataframe
        # remoteReadPath always follows format of sessionID/folderID/datasetName/
        # example: local/twitter-Tweet/trump/ => ['local','twitter-Tweet','trump','']
        filename = remoteReadPath.split('/')[-2] + '.csv'
        s3.downloadToDisk(filename, localReadPath, remoteReadPath)

        # quick fix for decoding error, sometimes the data is coded in ISO-8859-1
        # Array = 2D nested list holding column and row data
        Array = []
        try:
            with open(os.path.join(localReadPath, filename), 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        Array.append(row)
                except Exception as e:
                    print(e)
        except Exception:
            with open(os.path.join(localReadPath, filename), 'r', encoding='ISO-8859-1') as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        Array.append(row)
                except Exception as e:
                    print(e)

        # load to pandas dataframe
        df = pd.DataFrame(Array[1:], columns=Array[0])

        # user specify which column to; each row is a sentence, get a list of sentences
        self.sentences = df[df[column]!=''][column].dropna().astype('str').tolist()

        # combine sentences into a document
        self.text = ''.join(self.sentences)

    def plot(self):
        '''
        plot document sentiment score in a pie chart
        percentage of negative, neutral and positive
        '''
        if self.__documentSentiment_flag:
            labels = ['negative', 'neutral', 'positive']
            values = [self.scores['neg'], self.scores['neu'], self.scores['pos']]

            trace = go.Pie(labels=labels, values=values, textinfo='label+percent')
            div_sent = plot([trace],
                            output_type='div',
                            image='png',
                            auto_open=False,
                            image_filename='plot_img')
            fname_div_sent = 'div_sent.html'
            with open(os.path.join(self.localSavePath, fname_div_sent), 'w') as f:
                f.write(div_sent)
            s3.upload(self.localSavePath, self.awsPath, fname_div_sent)

            return s3.generate_downloads(self.awsPath, fname_div_sent)

        else:
            print('In order to plot the docuemtn sentiment,'
                  + 'you have to execute method documentSentiment first.')
            raise AttributeError

    def sentiment(self, algorithm='vader'):
        '''
        calculate sentence sentiment
        and store the list of scores in sentiment.csv
        '''

        sid = SentimentIntensityAnalyzer()

        result = [['sentence', 'negative', 'neutral', 'positive', 'compound']]

        if algorithm == 'vader':
            # sentence level
            for item in self.sentences:
                sent_scores = sid.polarity_scores(item)
                result.append([item.encode('utf-8', 'ignore'),
                               sent_scores['neg'],
                               sent_scores['neu'],
                               sent_scores['pos'],
                               sent_scores['compound']])

            # document level
            self.scores = sid.polarity_scores(self.text)

        elif algorithm == 'sentiWordNet':
            doc_pos_score = []
            doc_neg_score = []
            doc_obj_score = []

            # sentence level
            for sent in self.sentences:
                tokens = word_tokenize(sent)

                filtered_tokens = [word.lower() for word in tokens
                                   if (word.isalpha() == True
                                       and word.lower()
                                       not in stopwords.words('english'))]

                wnl = WordNetLemmatizer()
                processed_tokens = [wnl.lemmatize(word) for word in filtered_tokens]
                tagged = pos_tag(processed_tokens)

                # convert pos tag to sentiwordnet tag
                pos_score = []
                neg_score = []
                obj_score = []
                for tag in tagged:
                    word = tag[0].lower()
                    pos = self.pos_short(tag[1])

                    # calculate scores
                    senti_synset = list(swn.senti_synsets(word, pos))

                    if len(senti_synset) > 0:
                        # use the most common meaning, 0
                        pos_score.append(senti_synset[0].pos_score())
                        neg_score.append(senti_synset[0].neg_score())
                        obj_score.append(senti_synset[0].obj_score())
                # if valid
                if pos_score != [] or neg_score !=[] or obj_score !=[]:

                    doc_pos_score.append(self.average(pos_score))
                    doc_neg_score.append(self.average(neg_score))
                    doc_obj_score.append(self.average(obj_score))

                    result.append([sent.encode('utf-8', 'ignore'),
                                   self.average(neg_score),
                                   self.average(obj_score),
                                   self.average(pos_score),
                                   'NA'])

            # document level
            self.scores = {'neg': self.average(doc_neg_score),
                          'neu': self.average(doc_obj_score),
                          'pos': self.average(doc_pos_score)}


        # write sentence level senti scores
        fname = 'sentiment.csv'
        # quick fix for decoding error
        try:
            with open(os.path.join(self.localSavePath, fname), 'w',
                      newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(result)
                except UnicodeEncodeError as e:
                    print(e)
        except Exception:
            with open(os.path.join(self.localSavePath, fname), 'w',
                      newline='', encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(result)
                except UnicodeEncodeError as e:
                    print(e)
        s3.upload(self.localSavePath, self.awsPath, fname)

        # write document level senti scores
        fname_doc = 'document.json'
        with open(os.path.join(self.localSavePath, fname_doc), 'w') as f:
            json.dump(self.scores, f);
        s3.upload(self.localSavePath, self.awsPath, fname_doc)

        # set flag to true to indicate this document sentiment calculation has been carried out
        self.__documentSentiment_flag = True

        return s3.generate_downloads(self.awsPath, fname), s3.generate_downloads(self.awsPath, fname_doc)

    def negated(self):
        '''
        find if a sentence has negation word
        store the True/false per sentence to negation.csv
        '''
        negation_result = [['sentence', 'hasNegation']]
        for item in self.sentences:
            negation_result.append([item.encode('utf-8', 'ignore'), negated(item)])
        fname_negation = 'negation.csv'
        try:
            with open(os.path.join(self.localSavePath, fname_negation),
                      'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(negation_result)
                except UnicodeEncodeError:
                    print(e)
        except Exception:
            with open(os.path.join(self.localSavePath, fname_negation),
                      'w', newline='', encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(negation_result)
                except UnicodeEncodeError:
                    print(e)

        s3.upload(self.localSavePath, self.awsPath, fname_negation)

        return s3.generate_downloads(self.awsPath, fname_negation)

    def allcap(self):
        '''
        find if a sentence is composed of all capital letter
        store the True/False per sentence to allcap.csv
        '''
        allcap_result = [['sentence', 'ALL CAPITAL']]
        for item in self.sentences:
            allcap_result.append([item.encode('utf-8', 'ignore'),
                                  allcap_differential(item)])

        fname_allcap = 'allcap.csv'
        try:
            with open(os.path.join(self.localSavePath, fname_allcap),
                      'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(allcap_result)
                except UnicodeEncodeError as e:
                    print(e)
        except Exception:
            with open(os.path.join(self.localSavePath, fname_allcap),
                      'w', newline='', encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(allcap_result)
                except UnicodeEncodeError as e:
                    print(e)
        s3.upload(self.localSavePath, self.awsPath, fname_allcap)

        return s3.generate_downloads(self.awsPath, fname_allcap)

    ##########################################################################
    def average(self, score_list):
        """Get arithmetic average of scores."""
        if (score_list):
            # round to 4 decimals
            return round(sum(score_list) / float(len(score_list)), 4)

    def pos_short(self, pos):
        """Convert NLTK POS tags to SWN's POS tags."""
        if pos in set(['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']):
            return 'v'
        elif pos in set(['JJ', 'JJR', 'JJS']):
            return 'a'
        elif pos in set(['RB', 'RBR', 'RBS']):
            return 'r'
        elif pos in set(['NNS', 'NN', 'NNP', 'NNPS']):
            return 'n'
        else:
            return 'a'

def lambda_handler(event, context):
    '''
    entrance to invoke AWS lambda,
    variable event contains parameters passed in
    '''

    # patch to prevent old version of SMILE server breaks
    if 'algorithm' not in event.keys():
        event['algorithm'] = 'vader'

    output = dict()

    # arranging the paths
    awsPath = os.path.join(event['s3FolderName'], 'NLP', 'sentiment', event['uid'])

    # lambda offers an ephemeral disk capacity ("/tmp" space) of 512 MB
    localSavePath = os.path.join('/tmp', event['s3FolderName'], 'NLP', 'sentiment', event['uid'])
    localReadPath = os.path.join('/tmp', event['s3FolderName'], event['uid'])

    if not os.path.exists(localSavePath):
        os.makedirs(localSavePath)
    if not os.path.exists(localReadPath):
        os.makedirs(localReadPath)

    # set configuration file to store parameters
    fname = 'config.json'
    with open(os.path.join(localSavePath, fname), 'w') as f:
        json.dump(event, f)
    s3.upload(localSavePath, awsPath, fname)
    output['config'] = s3.generate_downloads(awsPath, fname)

    # construct sentiment analysis
    sentiment = Sentiment(awsPath, localSavePath, localReadPath,
                          event['remoteReadPath'], event['column'])
    output['sentiment'], output['doc'] = sentiment.sentiment(event['algorithm'])

    if event['algorithm'] == 'vader':
        output['negation'] = sentiment.negated()
        output['allcap']  = sentiment.allcap()

    output['div'] = sentiment.plot()

    # return a dictionary of {name:corresponding url}
    return output