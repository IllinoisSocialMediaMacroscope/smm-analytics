import nltk
from nltk import pos_tag, WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer, allcap_differential, negated
from nltk.tokenize import word_tokenize
from nltk.corpus import sentiwordnet as swn, stopwords
import csv
import plotly.graph_objs as go
from plotly.offline import plot
import pandas as pd
import json
import os
import writeToS3 as s3
import deleteDir as d
import notification as n
import argparse

class Sentiment:
    
    def __init__(self, awsPath, localSavePath, localReadPath, remoteReadPath, column):

            self.localSavePath = localSavePath
            self.awsPath = awsPath

            # download remote socialmedia data into a temp folder
            # load it into csv
            filename = remoteReadPath.split('/')[-2] + '.csv'
            s3.downloadToDisk(filename=filename,localpath=localReadPath, remotepath=remoteReadPath)
            
            Array = []
            try:
                with open(localReadPath + filename,'r',encoding="utf-8") as f:
                    reader = csv.reader(f)
                    try:
                        for row in reader:
                            Array.append(row)
                    except Exception as e:
                        pass
            except:
                with open(localReadPath + filename,'r',encoding="ISO-8859-1") as f:
                    reader = csv.reader(f)
                    try:
                        for row in reader:
                            Array.append(row)
                    except Exception as e:
                        pass
                    
            df = pd.DataFrame(Array[1:],columns=Array[0])
            self.sentences = df[df[column]!=''][column].dropna().astype('str').tolist()
            self.text = ''.join(self.sentences)
            
    
    def plot(self):
        labels = ['negative', 'neutral', 'positive']
        values = [self.scores['neg'], self.scores['neu'], self.scores['pos']]
        trace = go.Pie(labels=labels,values=values,textinfo='label+percent')
        
        div_sent = plot([trace], output_type='div',image='png',auto_open=False, image_filename='plot_img')
        fname_div_sent = 'div_sent.html'
        with open(self.localSavePath + fname_div_sent,"w") as f:
            f.write(div_sent)
        s3.upload(self.localSavePath,  self.awsPath, fname_div_sent)

        return s3.generate_downloads(self.awsPath, fname_div_sent)

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

    def negated(self):
        negation_result = [['sentence','hasNegation']]
        for item in self.sentences:
            negation_result.append([item.encode('utf-8','ignore'),negated(item)])
        fname_negation = 'negation.csv'
        try:
            with open(self.localSavePath + fname_negation, "w", newline='',encoding='utf-8') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(negation_result)
                except UnicodeEncodeError:
                    pass
        except:
            with open(self.localSavePath + fname_negation, "w", newline='',encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(negation_result)
                except UnicodeEncodeError:
                    pass
        s3.upload(self.localSavePath, self.awsPath, fname_negation)

        return s3.generate_downloads(self.awsPath, fname_negation)

    def allcap(self):
        allcap_result = [['sentence','ALL CAPITAL']]
        for item in self.sentences:
            allcap_result.append([item.encode('utf-8','ignore'),allcap_differential(item)])

        fname_allcap = 'allcap.csv'
        try:
            with open(self.localSavePath + fname_allcap, "w", newline='',encoding='utf-8') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(allcap_result)
                except UnicodeEncodeError:
                    pass
        except:
            with open(self.localSavePath + fname_allcap, "w", newline='',encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(allcap_result)
                except UnicodeEncodeError:
                    pass
        s3.upload(self.localSavePath, self.awsPath, fname_allcap)

        return s3.generate_downloads(self.awsPath, fname_allcap)
                          
   


if __name__ == '__main__':

    output = dict()

    parser = argparse.ArgumentParser(description="processing...")
    parser.add_argument('--remoteReadPath', required=True)
    parser.add_argument('--column',required=True)
    parser.add_argument('--s3FolderName',required=True)
    parser.add_argument('--email',required=True)
    parser.add_argument('--algorithm', required=False)
    parser.add_argument('--uid',required=True)
    parser.add_argument('--sessionURL',required=True)
    args = parser.parse_args()

    if args.algorithm == None:
        args.algorithm = 'vader'

    # arranging the paths
    awsPath = args.s3FolderName + '/NLP/sentiment/' + args.uid +'/'
    localSavePath = '/tmp/' + args.s3FolderName + '/NLP/sentiment/' + args.uid + '/'
    localReadPath = '/tmp/' + args.s3FolderName + '/' + args.uid + '/'
    if not os.path.exists(localSavePath):
        os.makedirs(localSavePath)
    if not os.path.exists(localReadPath):
        os.makedirs(localReadPath)
        
    fname = 'config.json'
    with open(localSavePath + fname,"w") as f:
        json.dump(vars(args),f)
    s3.upload(localSavePath, awsPath, fname)
    output['config'] = s3.generate_downloads(awsPath, fname)

    sentiment = Sentiment(awsPath, localSavePath, localReadPath, args.remoteReadPath, args.column)
    output['sentiment'], output['doc'] = sentiment.sentiment(args.algorithm)
    output['div'] = sentiment.plot()
 
    if args.algorithm == 'vader':
        output['negation'] = sentiment.negated()
        output['allcap']  = sentiment.allcap()

    d.deletedir('/tmp')
    n.notification(args.email,case=3,filename=awsPath,links=output,sessionURL=args.sessionURL)
