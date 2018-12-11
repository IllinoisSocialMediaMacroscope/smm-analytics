import csv
import pandas
import random
import os
from plotly.offline import plot
import plotly.graph_objs as go
from os.path import join, dirname
import json
import re
import writeToS3 as s3

class Classification:

<<<<<<< HEAD:lambda/lambda_classification_split/lambda_classification_split.py
    def __init__(self,awsPath, localSavePath, localReadPath, remoteReadPath, column):
=======
    def __init__(self,awsPath, localSavePath, localReadPath, remoteReadPath):
>>>>>>> 6e7945c8172aecd621036b560d98b7e2a0b55055:lambda/lambda_classification_split/lambda_classification_split.py

        self.localSavePath = localSavePath
        self.awsPath = awsPath

        # download remote socialmedia data into a temp folder
        # load it into csv
        filename = remoteReadPath.split('/')[-2] + '.csv'
        self.filename = filename # save it so split function can reuse this name
        s3.downloadToDisk(filename, localReadPath, remoteReadPath)
        
        Array = []
        try:
            with open(localReadPath + filename,'r',encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        Array.append(row)
                    except Exception as e:
                        pass
        except:
            with open(localReadPath + filename,'r',encoding='ISO-8859-1') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        Array.append(row)
                    except Exception as e:
                        pass

        df = pandas.DataFrame(Array[1:], columns=Array[0])

        # remoteReadPath always follows format of sessionID/folderID/datasetName/
        # example: local/GraphQL/twitter-Tweet/trump/ => ['local','GraphQL', 'twitter-Tweet','trump','']
        source = remoteReadPath.split('/')[2]

        # find the unique text in a corpus
        self.corpus = list(set(df[df[column] != ''][column].dropna().astype('str').tolist()))

        # strip http in the corpus
        self.corpus = [ re.sub(r"http\S+","",text) for text in self.corpus]

    def split(self,ratio):
        training_set = list(random.sample(self.corpus, int(len(self.corpus)*ratio/100)))
        testing_set = [item for item in self.corpus if item not in training_set]

        # plot a pie chart of the split
        labels = ['training set data points','unlabeled data points']
        values = [len(training_set), len(testing_set)]
        trace = go.Pie(labels=labels, values = values, textinfo='value')
        div_split = plot([trace], output_type='div',image='png',auto_open=False, image_filename='plot_img')
        fname_div_split = 'div_split.html'
        with open(self.localSavePath + fname_div_split,"w") as f:
            f.write(div_split)
        s3.upload(self.localSavePath, self.awsPath, fname_div_split)
        div_url = s3.generate_downloads(self.awsPath, fname_div_split)
        
        fname1 = 'TRAINING_' + self.filename
        try:
            with open(self.localSavePath + fname1,'w',newline="",encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['text','category'])
                for row in training_set:
                    try:
                        writer.writerow([row])
                    except UnicodeDecodeError:
                        pass
        except:
            with open(self.localSavePath + fname1,'w',newline="",encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                writer.writerow(['text','category'])
                for row in training_set:
                    try:
                        writer.writerow([row])
                    except UnicodeDecodeError:
                        pass
        s3.upload(self.localSavePath, self.awsPath, fname1)
        training_url = s3.generate_downloads(self.awsPath, fname1)



        fname2 = 'UNLABELED_' + self.filename
        try:
            with open(self.localSavePath + fname2,'w',newline="",encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['text'])
                for row in testing_set:
                    try:
                        writer.writerow([row])
                    except UnicodeDecodeError:
                        pass
        except:
            with open(self.localSavePath + fname2,'w',newline="",encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                writer.writerow(['text'])
                for row in testing_set:
                    try:
                        writer.writerow([row])
                    except UnicodeDecodeError:
                        pass
        s3.upload(self.localSavePath, self.awsPath, fname2)
        unlabeled_url = s3.generate_downloads(self.awsPath, fname2)


        return {'div': div_url, 'training':training_url, 'testing': unlabeled_url}


def lambda_handler(event,context):

    output = dict()

    # arranging the paths
    awsPath = event['s3FolderName'] + '/ML/classification/' + event['uid'] +'/'
    localSavePath = '/tmp/' + event['s3FolderName'] + '/ML/classification/' + event['uid'] + '/'
    localReadPath = '/tmp/' + event['s3FolderName'] + '/'
    if not os.path.exists(localSavePath):
        os.makedirs(localSavePath)
    if not os.path.exists(localReadPath):
        os.makedirs(localReadPath)

    fname = 'config.json'
    with open(localSavePath + fname,"w") as f:
        json.dump(event,f)
    s3.upload(localSavePath, awsPath, fname)
    output['config'] = s3.generate_downloads(awsPath, fname)
    output['uuid'] = event['uid']    

<<<<<<< HEAD:lambda/lambda_classification_split/lambda_classification_split.py
    classification = Classification(awsPath, localSavePath, localReadPath, event['remoteReadPath'], event['column'])
=======
    classification = Classification(awsPath, localSavePath, localReadPath, event['remoteReadPath'])
>>>>>>> 6e7945c8172aecd621036b560d98b7e2a0b55055:lambda/lambda_classification_split/lambda_classification_split.py
    output.update(classification.split(int(event['ratio'])))

    return output