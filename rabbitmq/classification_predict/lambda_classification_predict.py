import csv
import os
import sklearn
import pickle
from plotly.offline import plot
import plotly.graph_objs as go
from collections import Counter
import writeToS3 as s3

class Classification:

    def __init__(self, awsPath, localSavePath):

        self.localSavePath = localSavePath
        self.awsPath = awsPath

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
        div_category = plot([trace], output_type='div',image='png',auto_open=False, image_filename='plot_img')

        fname_div_category = 'div_category.html'
        with open(self.localSavePath + fname_div_category,"w") as f:
            f.write(div_category)
        s3.upload(self.localSavePath, self.awsPath, fname_div_category)
        return s3.generate_downloads(self.awsPath, fname_div_category)
