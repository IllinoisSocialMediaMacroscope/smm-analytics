import csv
import os
import pandas as pd
import zipfile
from writeToS3 import WriteToS3

class Dataset:

    def __init__(self, HOST_IP=None, AWS_ACCESSKEY=None, AWS_ACCESSKEYSECRET=None, BUCKET_NAME=None):
        self.s3 = WriteToS3(HOST_IP, AWS_ACCESSKEY, AWS_ACCESSKEYSECRET, BUCKET_NAME)

    def organize_path_lambda(self, event):
        """
        parse the lambda handler parameter event to construct necessary paths for reading and storing data
        :param event: aws lambda parameters from handler
        :return: path dictionary
        """
        # arranging the paths
        remoteReadPath = event['remoteReadPath']
        localReadPath = os.path.join('/tmp', remoteReadPath)
        localSavePath = os.path.join('/tmp', remoteReadPath)
        remoteSavePath = os.path.join(remoteReadPath)
        filename = remoteReadPath.split('/')[-2] + '.csv'

        if not os.path.exists(localSavePath):
            os.makedirs(localSavePath)
            os.makedirs(os.path.join(localSavePath, 'img'))
        if not os.path.exists(localReadPath):
            os.makedirs(localReadPath)

        path = {
            'remoteReadPath': remoteReadPath,
            'localReadPath': localReadPath,
            'localSavePath': localSavePath,
            'remoteSavePath': remoteSavePath,
            'filename': filename
        }

        return path


    def get_remote_input(self, remoteReadPath, filename, localReadPath):
        """
        download input file from s3 bucket to a local location, and then load
        it to a pandas dataframe
        :param remoteReadPath: remote path in s3 to store the data
        :param localReadPath: local location to store the data, usually in /tmp
        :return: df: dataframe that contains the complete input file
        """
        self.s3.downloadToDisk(filename, localReadPath, remoteReadPath)

        # quick fix for decoding error, sometimes the data is coded in ISO-8859-1
        # Array = 2D nested list holding column and row data
        Array = []
        try:
            with open(os.path.join(localReadPath, filename), 'r',
                      encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        Array.append(row)
                except Exception as e:
                    print(e)
        except Exception:
            with open(os.path.join(localReadPath, filename), 'r',
                      encoding='ISO-8859-1') as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        Array.append(row)
                except Exception as e:
                    print(e)

        # load to pandas dataframe
        df = pd.DataFrame(Array[1:], columns=Array[0])

        return df


    def save_local_output(self, localSavePath, fname, output_data):
        with open(os.path.join(localSavePath, 'img', fname), 'wb') as f:
            f.write(output_data)


    def zipdir(self, path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                print(file)
                ziph.write(os.path.join(root, file), file)


    def save_remote_output(self, localSavePath, remoteSavePath, fname):
        """

        :param localSavePath:
        :param remoteSavePath:
        :param fname:
        :param output_data:
        :return:
        """
        zipf = zipfile.ZipFile(os.path.join(localSavePath, fname), 'w',
                               zipfile.ZIP_DEFLATED)
        self.zipdir(os.path.join(localSavePath,'img'), zipf)
        zipf.close()

        self.s3.upload(localSavePath, remoteSavePath, fname)
        url = self.s3.generate_downloads(remoteSavePath, fname)

        return url
