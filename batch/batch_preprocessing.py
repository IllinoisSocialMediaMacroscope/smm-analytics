import nltk
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer, Text, FreqDist, pos_tag_sents,pos_tag, PorterStemmer
import csv
import plotly.graph_objs as go
from plotly import tools
from plotly.offline import plot
import pandas as pd
import re, string
import json
import os
from os.path import dirname
import writeToS3 as s3
import deleteDir as d
import notification as n
import argparse

class Preprocess:

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
            sentences = df[df[column]!=''][column].dropna().astype('str').tolist()
            sentences = [ re.sub(r"http\S+","",tweet) for tweet in sentences]
            self.sentences = sentences




    def get_phrases(self):
            # get Phrases
            phrases = []
            puncList = '.;,:!?/\\)(\"\''
            regex = re.compile('[%s%s]' % (puncList,'|\t\n'))
            for item in self.sentences:
                for i in regex.split(item):
                    if i != '' and i.isdigit()==False and len(i)>20:
                        phrases.append(i.lower())
            phrases.insert(0,'Phrase')

            fname_phrases = 'sentence.csv'
            try:
                with open(self.localSavePath + fname_phrases, "w", newline='',encoding='utf-8') as f:
                    for item in phrases:
                        try:
                            f.write("{}\n".format(item)) 
                        except UnicodeEncodeError:
                            pass
            except:
                with open(self.localSavePath + fname_phrases, "w", newline='',encoding='ISO-8859-1') as f:
                    for item in phrases:
                        try:
                            f.write("{}\n".format(item)) 
                        except UnicodeEncodeError:
                            pass
            s3.upload(self.localSavePath, self.awsPath, fname_phrases)

            return s3.generate_downloads(self.awsPath, fname_phrases)




    def get_words(self, source):
            if source == 'twitter-Tweet' or source == 'twitter-Stream' or source == 'crimson-Hexagon':
                tknz = TweetTokenizer()
            else:
                #tknz = tokenizer.RedditTokenizer()
                tknz = TweetTokenizer()
            self.tokens = [tknz.tokenize(t) for t in self.sentences]
                
            # nltk's stopwords are too weak
            with open('/scripts/stopwords_en.txt','r') as f:
                stopwords2 = f.read().split('\n')
            with open('/scripts/twitter-customized.txt','r') as f:
                stopwords3 = f.read().split(',')

            self.filtered_tokens_lower = []
            self.filtered_tokens = []
            for token in self.tokens:
                self.filtered_tokens.append([word for word in token if (word.lower() not in stopwords.words('english')) #nltk stopwords
                                             and (word.lower() not in stopwords2) # third party stopwors:https://sites.google.com/site/kevinbouge/stopwords-lists
                                             and (word.isalpha() == True or word[0] == '#' or word[0] == '$')      # only english characters
                                             and (word.lower() not in stopwords3) ])  # twitter specific stopwordshttps://sites.google.com/site/iamgongwei/home/sw
                self.filtered_tokens_lower.append([word.lower() for word in token if (word.lower() not in stopwords.words('english'))
                                             and (word.lower() not in stopwords2)
                                             and (word.isalpha() == True or word[0] == '#' or word[0] == '$')
                                             and (word.lower() not in stopwords3) ])

            fname_filtered = 'tokenized.csv'
            try:
                with open(self.localSavePath + fname_filtered, "w", newline='',encoding='utf-8') as f:
                    writer = csv.writer(f)
                    try:
                        writer.writerows(self.filtered_tokens_lower)
                    except UnicodeEncodeError:
                        pass
            except:
                with open(self.localSavePath + fname_filtered, "w", newline='',encoding='ISO-8859-1') as f:
                    writer = csv.writer(f)
                    try:
                        writer.writerows(self.filtered_tokens_lower)
                    except UnicodeEncodeError:
                        pass
            s3.upload(self.localSavePath, self.awsPath,fname_filtered)

            return s3.generate_downloads(self.awsPath,fname_filtered)



          
        

    def stem_lematize(self,process):

        if process == 'lemmatization':
            wnl = WordNetLemmatizer()
            self.processed_tokens = []
            for tk in self.filtered_tokens_lower:
                self.processed_tokens.append([wnl.lemmatize(t) for t in tk])

            fname_processed = 'lemmatized.csv'
            try:
                with open(self.localSavePath + fname_processed, "w", newline='',encoding='utf-8') as f:
                    writer = csv.writer(f)
                    try:
                        writer.writerows(self.processed_tokens)
                    except UnicodeEncodeError:
                        pass
            except:
                with open(self.localSavePath + fname_processed, "w", newline='',encoding='ISO-8859-1') as f:
                    writer = csv.writer(f)
                    try:
                        writer.writerows(self.processed_tokens)
                    except UnicodeEncodeError:
                        pass
            s3.upload(self.localSavePath, self.awsPath,fname_processed)

            return s3.generate_downloads(self.awsPath,fname_processed)

        elif process == 'stemming':
            porter = PorterStemmer()
            self.processed_tokens = []
            for tk in self.filtered_tokens_lower:
                self.processed_tokens.append([porter.stem(t) for t in tk])
                
            fname_processed = 'stemmed.csv'
            try:
                with open(self.localSavePath + fname_processed, "w", newline='',encoding='utf-8') as f:
                    writer = csv.writer(f)
                    try:
                        writer.writerows(self.processed_tokens)
                    except UnicodeEncodeError:
                        pass
            except:
                with open(self.localSavePath + fname_processed, "w", newline='',encoding='ISO-8859-1') as f:
                    writer = csv.writer(f)
                    try:
                        writer.writerows(self.processed_tokens)
                    except UnicodeEncodeError:
                        pass
            s3.upload(self.localSavePath, self.awsPath,fname_processed)

            return s3.generate_downloads(self.awsPath,fname_processed)

        elif process == 'both':
            wnl = WordNetLemmatizer()
            porter = PorterStemmer()
            self.processed_tokens = []

            for tk in self.filtered_tokens_lower:
                self.processed_tokens.append([wnl.lemmatize(porter.stem(t)) for t in tk])

            fname_processed = 'lemmatized-stemmed.csv'
            try:
                with open(self.localSavePath + fname_processed, "w", newline='',encoding='utf-8') as f:
                    writer = csv.writer(f)
                    try:
                        writer.writerows(self.processed_tokens)
                    except UnicodeEncodeError:
                        pass
            except:
                with open(self.localSavePath + fname_processed, "w", newline='',encoding='ISO-8859-1') as f:
                    writer = csv.writer(f)
                    try:
                        writer.writerows(self.processed_tokens)
                    except UnicodeEncodeError:
                        pass
            s3.upload(self.localSavePath, self.awsPath,fname_processed)
            return s3.generate_downloads(self.awsPath,fname_processed)
            



    def tagging(self,tagger):
        if tagger == 'posTag':
            self.pos_tagging()

        fname_tagged = 'POStagged.csv'
        try:
            with open(self.localSavePath + fname_tagged, "w", newline='',encoding='utf-8') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(self.tag)
                except UnicodeEncodeError:
                    pass
        except:
            with open(self.localSavePath + fname_tagged, "w", newline='',encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                try:
                    writer.writerows(self.tag)
                except UnicodeEncodeError:
                    pass
        s3.upload(self.localSavePath, self.awsPath,fname_tagged)
        return s3.generate_downloads(self.awsPath,fname_tagged)

    def pos_tagging(self):
        self.tag = []
        self.tag = pos_tag_sents(self.processed_tokens)

        
       
    def plotFreq(self):

        filtered_document = []
        for sent_token in self.filtered_tokens:
            filtered_document += sent_token
        processed_document = []
        for sent_token in self.processed_tokens:
            processed_document += sent_token

        # use plotly instead
        filtered_most_common = FreqDist(filtered_document).most_common()
        fname_most_common = 'frequent-rank.csv'
        try:
            with open(self.localSavePath + fname_most_common, "w", newline='',encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['word','frequency'])
                try:
                    writer.writerows(filtered_most_common)
                except UnicodeEncodeError:
                    pass
        except:
            with open(self.localSavePath + fname_most_common, "w", newline='',encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                writer.writerow(['word','frequency'])
                try:
                    writer.writerows(filtered_most_common)
                except UnicodeEncodeError:
                    pass
        s3.upload(self.localSavePath, self.awsPath,fname_most_common)
        most_common_url = s3.generate_downloads(self.awsPath,fname_most_common)
              
        processed_most_common = FreqDist(processed_document).most_common()
        # word frequency figure
        filtered_X = []
        filtered_y = []
        processed_X = []
        processed_y =[]

        for common in filtered_most_common[:25]:  
            filtered_X.append(common[0])
            filtered_y.append(common[1])
        for common in processed_most_common[:25]:  
            processed_X.append(common[0])
            processed_y.append(common[1])

        trace0 = go.Bar(x=filtered_X,
                        y=filtered_y,
                        marker=dict(color='rgba(200,75,73,1.0)',
                        line=dict(color='rgba(111,11,9,1.0)',
                                  width=1),
                        ),
                        name='tokenized words',
                        #orientation='h',
                    )
        trace1 = go.Bar(x=processed_X,
                        y=processed_y,
                        marker=dict(color='rgba(66,139,202,1.0)',
                        line=dict(color='rgba(1,52,97,1.0)',
                                  width=1),
                        ),
                        name='stemmed and (or) lemmatized words',
                        #orientation='h',
                    )
        layout = dict(
            title='Top 25 frequent words',
            font=dict(family='Arial',size=12),
            yaxis1=dict(
                showgrid=False,
                showline=True,
                showticklabels=True,
                linecolor='rgba(102, 102, 102, 0.8)',
                linewidth=2,
                domain=[0.15, 0.85],
            ),
            yaxis2=dict(
                showgrid=False,
                showline=True,
                showticklabels=True,
                linecolor='rgba(102, 102, 102, 0.8)',
                linewidth=2,
                domain=[0.15, 0.85],
            ),
           xaxis1=dict(
                zeroline=False,
                showline=False,
                showticklabels=True,
                showgrid=True,
                domain=[0, 0.45],
            ),
            xaxis2=dict(
                zeroline=False,
                showline=False,
                showticklabels=True,
                showgrid=True,
                domain=[0.55, 1],
            ),
            legend=dict(
                x=0.029,
                y=1.038,
                font=dict(
                 size=15,
            ),
        ),
            margin=dict(
                l=70,
                r=70,
                t=70,
                b=70,
            )
        )

        annotations=[]
        for x1,y1,x2,y2 in zip(filtered_X, filtered_y, processed_X, processed_y):
            annotations.append(dict(xref='x1',yref='y1',
                                    y=y1+2, x=x1,
                                    text=str(y1),
                                    font=dict(family='Arial',
                                    size=12,
                                    color='rgba(200,75,73,1.0)'),
                                    showarrow=False))
            annotations.append(dict(xref='x2',yref='y2',
                                    y=y2+2, x=x2,
                                    text=str(y2),
                                    font=dict(family='Arial',
                                    size=12,
                                    color='rgba(66,139,202,1.0)'),
                                    showarrow=False))

        layout['annotations'] = annotations
                                    

        fig = tools.make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
                          shared_yaxes=False, vertical_spacing=0.001,print_grid=False)
        fig.append_trace(trace0, 1, 1)
        fig.append_trace(trace1, 1, 2)
        fig['layout'].update(layout)
        
        div = plot(fig, output_type='div',image='png',auto_open=False, image_filename='plot_img')
        fname_div = 'div.html'
        with open(self.localSavePath + fname_div,"w") as f:
            f.write(div)
        s3.upload(self.localSavePath, self.awsPath,fname_div)
        div_url = s3.generate_downloads(self.awsPath,fname_div)

        return {'most_common': most_common_url, 'div':div_url}


if __name__ == '__main__':

    output = dict()

    parser = argparse.ArgumentParser(description="processing...")
    parser.add_argument('--remoteReadPath', required=True)
    parser.add_argument('--column',required=True)
    parser.add_argument('--source',required=True)
    parser.add_argument('--process',required=True)
    parser.add_argument('--tagger',required=True)
    parser.add_argument('--s3FolderName',required=True)
    parser.add_argument('--email',required=True)
    parser.add_argument('--uid',required=True)
    parser.add_argument('--sessionURL',required=True)
    args = parser.parse_args()

    # arranging the paths
    awsPath = args.s3FolderName + '/NLP/preprocessing/' + args.uid +'/'
    localSavePath = '/tmp/' + args.s3FolderName + '/NLP/preprocessing/' + args.uid + '/'
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
    
    
    preprocessing = Preprocess(awsPath, localSavePath, localReadPath, args.remoteReadPath, args.column)
    output['phrases'] = preprocessing.get_phrases()

    # parse the path to get the source
    source = args.remoteReadPath.split('/')[2]
	
    output['filtered'] = preprocessing.get_words(source)
    output['processed'] = preprocessing.stem_lematize(args.process)
    
    plot = preprocessing.plotFreq()
    output['div'] = plot['div']
    output['most_common'] = plot['most_common']
    
    output['tagged'] = preprocessing.tagging(args.tagger)

    d.deletedir('/tmp')
    n.notification(args.email,case=3,filename=awsPath,links=output,sessionURL=args.sessionURL)




