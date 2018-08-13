import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer,allcap_differential,negated
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
    sid = SentimentIntensityAnalyzer()
    
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
            self.sent = df[df[column]!=''][column].dropna().astype('str').tolist()
            self.text = ''.join(self.sent)
            
    
    def plot(self):
        self.scores = self.sid.polarity_scores(self.text)
        labels = ['negative', 'neutral', 'positive']
        values = [self.scores['neg'], self.scores['neu'], self.scores['pos']]
        trace = go.Pie(labels=labels,values=values,textinfo='label+percent')
        
        div_sent = plot([trace], output_type='div',image='png',auto_open=False, image_filename='plot_img')
        fname_div_sent = 'div_sent.html'
        with open(self.localSavePath + fname_div_sent,"w") as f:
            f.write(div_sent)
        s3.upload(self.localSavePath,  self.awsPath, fname_div_sent)

        return s3.generate_downloads(self.awsPath, fname_div_sent)



    def documentSentiment(self):
        
	# Save scores into json
        fname_doc = 'document.json'
        with open(self.localSavePath + fname_doc,"w") as f:
            json.dump(self.scores,f);
        s3.upload(self.localSavePath,  self.awsPath, fname_doc)

        return s3.generate_downloads(self.awsPath, fname_doc)


		
		
    def sentenceSentiment(self):
        result = [['sentence','negative','neutral','positive','compound']]
        for item in self.sent:
            sent_scores = self.sid.polarity_scores(item)
            result.append([item.encode('utf-8','ignore'),sent_scores['neg'],sent_scores['neu'],sent_scores['pos'],sent_scores['compound']])

        fname = 'sentiment.csv'
        try:
            with open(self.localSavePath + fname, "w", newline='',encoding='utf-8') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(result)
                except UnicodeEncodeError:
                    pass
        except:
            with open(self.localSavePath + fname, "w", newline='',encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(result)
                except UnicodeEncodeError:
                    pass
        s3.upload(self.localSavePath, self.awsPath, fname)

        return s3.generate_downloads(self.awsPath, fname)
        




    def negated(self):
        negation_result = [['sentence','hasNegation']]
        for item in self.sent:
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
        for item in self.sent:
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
    parser.add_argument('--uid',required=True)
    parser.add_argument('--sessionURL',required=True)
    args = parser.parse_args()

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
    output['div'] = sentiment.plot()
    output['doc'] = sentiment.documentSentiment()
    output['sentiment'] = sentiment.sentenceSentiment()
    output['negation'] = sentiment.negated()
    output['allcap']  = sentiment.allcap()

    d.deletedir('/tmp')
    n.notification(args.email,case=3,filename=awsPath,links=output,sessionURL=args.sessionURL)
