import csv
import os
from os.path import join, dirname
import pickle
import numpy as np
from plotly.offline import plot
import plotly.graph_objs as go
from collections import Counter
import json
import writeToS3 as s3
import argparse
import deleteDir as d
import notification as n

class Classification:

    def __init__(self, awsPath, localSavePath, filename):

        self.localSavePath = localSavePath
        self.awsPath = awsPath
        self.filename = filename

    def predict(self):

        # load classification model
        pkl_model = os.path.join(self.localSavePath,'classification_pipeline.pickle')
        with open(pkl_model,'rb') as f:
            text_clf = pickle.load(f)

        # load text set
        data = []
        try:
            with open(self.localSavePath + 'UNLABELED_' + self.filename + '.csv','r',encoding='utf-8') as f:
                reader = list(csv.reader(f))
                for row in reader[1:]:
                    try:
                        data.extend(row)
                    except Exception as e:
                        pass
        except:
            with open(self.localSavePath + 'UNLABELED_' + self.filename + '.csv','r',encoding='ISO-8859-1') as f:
                reader = list(csv.reader(f))
                for row in reader[1:]:
                    try:
                        data.extend(row)
                    except Exception as e:
                        pass

        # predict using trained model         
        self.predicted = text_clf.predict(data)

        # save result
        fname = 'PREDICTED_' + self.filename + '.csv'
        try:
            with open(self.localSavePath + fname,'w',newline="",encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['text','category'])
                for i in range(len(data)):
                    try:
                        writer.writerow([data[i],self.predicted[i]])
                    except:
                        pass
        except:
            with open(self.localSavePath + fname,'w',newline="",encoding='ISO-8859-1') as f:
                writer = csv.writer(f)
                writer.writerow(['text','category'])
                for i in range(len(data)):
                    try:
                        writer.writerow([data[i],self.predicted[i]])
                    except:
                        pass
        s3.upload(self.localSavePath, self.awsPath, fname)
        return s3.generate_downloads(self.awsPath, fname)
        

    def plot(self):
        y_pred_dict = Counter(self.predicted)
        labels = []
        values = []
        for i in y_pred_dict.keys():
            labels.append("class: " + str(i))
            values.append(y_pred_dict[i])
        trace = go.Pie(labels=labels, values = values, textinfo='label')
        div_comp = plot([trace], output_type='div',image='png',auto_open=False, image_filename='plot_img')

        fname_div_comp = 'div_comp.html'
        with open(self.localSavePath + fname_div_comp,"w") as f:
            f.write(div_comp)
        s3.upload(self.localSavePath, self.awsPath, fname_div_comp)
        return s3.generate_downloads(self.awsPath, fname_div_comp)

        

if __name__ == '__main__':

    output = dict()

    parser = argparse.ArgumentParser(description="processing...")
    parser.add_argument('--remoteReadPath', required=True)
    parser.add_argument('--uuid',required=True)
    parser.add_argument('--s3FolderName',required=True)
    parser.add_argument('--email',required=True)
    args = parser.parse_args()
    
    uid = args.uuid
    awsPath = args.s3FolderName + '/ML/classification/' + uid +'/'
    localSavePath = '/tmp/' + args.s3FolderName + '/ML/classification/' + uid + '/'
    if not os.path.exists(localSavePath):
        os.makedirs(localSavePath)
    if not os.path.exists(localSavePath):
        os.makedirs(localSavePath)

    # download config to local folder
    fname_config = 'config.json'
    if s3.checkExist(awsPath, fname_config):
        s3.downloadToDisk(fname_config, localSavePath, awsPath)
        with open(localSavePath + fname_config, "r") as fp:
            data = json.load(fp)
            for key in vars(args).keys():
                if key not in data.keys():
                    data[key] = vars(args)[key]
        with open(localSavePath + fname_config,"w") as f:
            json.dump(data,f)
        s3.upload(localSavePath, awsPath, fname_config)
        output['config'] = s3.generate_downloads(awsPath, fname_config)
        output['uuid'] = uid

    else:
        raise ValueError('This session ID is invalid!')
        exit()
        

    # download unlabeled data to local folder
    filename = args.remoteReadPath.split('/')[-2]
    fname_unlabeled = 'UNLABELED_' + filename +'.csv'
    if s3.checkExist(awsPath, fname_unlabeled): 
        s3.downloadToDisk(fname_unlabeled, localSavePath, awsPath)
    else:
        raise ValueError('You\'re requesting ' + fname_unlabeled + ' file, and it\'s not found in your remote directory!\
            It is likely that you have not yet performed step 1 -- split the dataset into training and predicting set, or you have provided the wrong sessionID.')
        exit()

    #download pickle model to local folder
    fname_pickle = 'classification_pipeline.pickle'
    if s3.checkExist(awsPath, fname_pickle): 
        s3.downloadToDisk(fname_pickle, localSavePath, awsPath)
    else:
        raise ValueError('You\'re requesting ' + fname_pickle + ' file, and it\'s not found in your remote directory! \
            It is likely that you have not yet performed step 2 -- model training, or you have provided the wrong sessionID.')
        exit()

    
    classification = Classification(awsPath, localSavePath, filename)
    output['predict'] = classification.predict()
    output['div'] = classification.plot()

    d.deletedir('/tmp')
    n.notification(args.email,case=3,filename=awsPath)

