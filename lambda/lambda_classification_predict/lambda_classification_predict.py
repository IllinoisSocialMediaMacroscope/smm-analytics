import csv
import json
import os
import pickle
from collections import Counter

import plotly.graph_objs as go
from plotly.offline import plot
from writeToS3 import WriteToS3


class Classification:

    def __init__(self, s3, awsPath, localSavePath):

        self.localSavePath = localSavePath
        self.awsPath = awsPath
        self.s3 = s3

    def predict(self):

        # load classification model
        pkl_model = os.path.join(self.localSavePath,'pipeline.pickle')
        with open(pkl_model,'rb') as f:
            text_clf = pickle.load(f)

        # load text set
        data = []
        try:
            with open(self.localSavePath + 'testing.csv','r',encoding='utf-8',
                      errors="ignore") as f:
                reader = list(csv.reader(f))
                for row in reader[1:]:
                    try:
                        data.extend(row)
                    except Exception as e:
                        pass
        except:
            with open(self.localSavePath + 'testing.csv','r',encoding='ISO-8859-1',
                      errors="ignore") as f:
                reader = list(csv.reader(f))
                for row in reader[1:]:
                    try:
                        data.extend(row)
                    except Exception as e:
                        pass

        # predict using trained model         
        self.predicted = text_clf.predict(data)

        # save result
        fname = 'predicting.csv'
        try:
            with open(self.localSavePath + fname,'w',newline="",encoding='utf-8',
                      errors="ignore") as f:
                writer = csv.writer(f)
                writer.writerow(['text','category'])
                for i in range(len(data)):
                    try:
                        writer.writerow([data[i],self.predicted[i]])
                    except:
                        pass
        except:
            with open(self.localSavePath + fname,'w',newline="",encoding='ISO-8859-1',
                      errors="ignore") as f:
                writer = csv.writer(f)
                writer.writerow(['text','category'])
                for i in range(len(data)):
                    try:
                        writer.writerow([data[i],self.predicted[i]])
                    except:
                        pass
        self.s3.upload(self.localSavePath, self.awsPath, fname)
        return self.s3.generate_downloads(self.awsPath, fname)
        

    def plot(self):
        y_pred_dict = Counter(self.predicted)
        labels = []
        values = []
        for i in y_pred_dict.keys():
            labels.append("class: " + str(i))
            values.append(y_pred_dict[i])
        trace = go.Pie(labels=labels, values = values, textinfo='label')
        div_category = plot([trace], output_type='div',image='png',auto_open=False, image_filename='plot_img')

        fname_div_category = 'div_category.html'
        with open(self.localSavePath + fname_div_category,"w") as f:
            f.write(div_category)
        self.s3.upload(self.localSavePath, self.awsPath, fname_div_category)
        return self.s3.generate_downloads(self.awsPath, fname_div_category)

        

def lambda_handler(event,context):
    if 'HOST_IP' in event.keys():
        HOST_IP = event['HOST_IP']
    else:
        HOST_IP = None

    if 'AWS_ACCESSKEY' in event.keys():
        AWS_ACCESSKEY = event['AWS_ACCESSKEY']
    else:
        AWS_ACCESSKEY = None

    if 'AWS_ACCESSKEYSECRET' in event.keys():
        AWS_ACCESSKEYSECRET = event['AWS_ACCESSKEYSECRET']
    else:
        AWS_ACCESSKEYSECRET = None

    if 'BUCKET_NAME' in event.keys():
        BUCKET_NAME = event['BUCKET_NAME']
    else:
        BUCKET_NAME = None

    s3 = WriteToS3(HOST_IP, AWS_ACCESSKEY, AWS_ACCESSKEYSECRET, BUCKET_NAME)
    output = dict()

    uid = event['uid']
    awsPath = event['s3FolderName'] + '/ML/classification/' + uid +'/'
    localSavePath = '/tmp/' + event['s3FolderName'] + '/ML/classification/' + uid + '/'
    if not os.path.exists(localSavePath):
        os.makedirs(localSavePath)
    if not os.path.exists(localSavePath):
        os.makedirs(localSavePath)

    # download config to local folder
    fname_config = 'config.json'
    try:
        s3.downloadToDisk(fname_config, localSavePath, awsPath)
        with open(localSavePath + fname_config, "r") as fp:
            data = json.load(fp)
            for key in data.keys():
                if key not in event.keys():
                    event[key] = data[key]
        with open(localSavePath + fname_config,"w") as f:
            json.dump(event,f)
        s3.upload(localSavePath, awsPath, fname_config)
        output['config'] = s3.generate_downloads(awsPath, fname_config)
        output['uid'] = uid

    except:
        raise ValueError('This session ID is invalid!')
        exit()
        

    # download unlabeled data to local folder
    fname_unlabeled = 'testing.csv'
    try: 
        s3.downloadToDisk(fname_unlabeled, localSavePath, awsPath)
    except:
        raise ValueError('You\'re requesting ' + fname_unlabeled + ' file, and it\'s not found in your remote directory!\
            It is likely that you have not yet performed step 1 -- split the dataset into training and predicting set, or you have provided the wrong sessionID.')
        exit()

    #download pickle model to local folder
    fname_pickle = 'pipeline.pickle'
    try: 
        s3.downloadToDisk(fname_pickle, localSavePath, awsPath)
    except:
        raise ValueError('You\'re requesting ' + fname_pickle + ' file, and it\'s not found in your remote directory! \
            It is likely that you have not yet performed step 2 -- model training, or you have provided the wrong sessionID.')
        exit()

    classification = Classification(s3, awsPath, localSavePath)
    output['predicting'] = classification.predict()
    output['div_category'] = classification.plot()


    return output
