import csv
import os
import json
import pickle
import pandas as pd
import types
from writeToS3 import WriteToS3

class Dataset:

    def __init__(self, MINIO_URL=None, AWS_ACCESSKEY=None, AWS_ACCESSKEYSECRET=None, BUCKET_NAME=None):
        self.s3 = WriteToS3(MINIO_URL, AWS_ACCESSKEY, AWS_ACCESSKEYSECRET, BUCKET_NAME)

    def organize_path_lambda(self, event):
        """
        parse the lambda handler parameter event to construct necessary paths for reading and storing data
        :param event: aws lambda parameters from handler
        :return: path dictionary
        """
        # arranging the paths
        localReadPath = os.path.join('/tmp', event['s3FolderName'], event['uid'])
        localSavePath = os.path.join('/tmp',
                                     event['s3FolderName'] + event['resultPath'],
                                     event['uid'])
        remoteSavePath = os.path.join(event['s3FolderName'] + event['resultPath'],
                                      event['uid'])
        if 'remoteReadPath' not in event.keys() or event['remoteReadPath'] == 'undefined':
            remoteReadPath = remoteSavePath
            filename = event['labeledFilename']
        else:
            remoteReadPath = event['remoteReadPath']
            filename = remoteReadPath.split('/')[-2] + '.csv'

        if not os.path.exists(localSavePath):
            os.makedirs(localSavePath)
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
                      encoding='utf-8', errors="ignore") as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        Array.append(row)
                except Exception as e:
                    print(e)
        except Exception:
            with open(os.path.join(localReadPath, filename), 'r',
                      encoding='ISO-8859-1', errors="ignore") as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        Array.append(row)
                except Exception as e:
                    print(e)

        # load to pandas dataframe
        df = pd.DataFrame(Array[1:], columns=Array[0])

        return df


    def save_remote_output(self, localSavePath, remoteSavePath, fname, output_data):
        """
        save output in memory first to local file, then upload to remote S3 bucket
        :param localSavePath: local saved file
        :param remoteSavePath: remote save file path
        :param fname: filename
        :param output_data: the actual data
        :return: url of the file saved in S3 bucket
        """

        # json
        if isinstance(output_data, dict):
            fname += '.json'
            with open(os.path.join(localSavePath, fname), 'w') as f:
                json.dump(output_data, f)

        # dataframe to csv
        elif isinstance(output_data, pd.DataFrame):
            fname += '.csv'
            output_data.to_csv(fname, encoding='utf-8')

        # string to html
        elif isinstance(output_data, str):
            fname += '.html'
            with open(os.path.join(localSavePath, fname), 'w') as f:
                f.write(output_data)

        # list(list) to csv
        elif isinstance(output_data, list) \
                and (isinstance(output_data[0], list) or isinstance(output_data[0],
                                                                    tuple)):
            fname += '.csv'
            with open(os.path.join(localSavePath, fname), 'w', newline='',
                      encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in output_data:
                    try:
                        writer.writerow(row)
                    except UnicodeEncodeError as e:
                        print(e)

        # special case
        elif isinstance(output_data, types.GeneratorType):
            if fname == 'gephi':
                fname += '.gml'
            elif fname == 'pajek':
                fname += '.net'
            else:
                fname += '.unknown'

            with open(os.path.join(localSavePath, fname), 'w', newline='',
                      encoding='utf-8') as f:
                for line in output_data:
                    f.write(line + '\n')

        # else pickle the object
        else:
            fname += '.pickle'
            with open(os.path.join(localSavePath, fname), 'wb') as f:
                pickle.dump(output_data, f)

        self.s3.upload(localSavePath, remoteSavePath, fname)
        url = self.s3.generate_downloads(remoteSavePath, fname)

        return url
