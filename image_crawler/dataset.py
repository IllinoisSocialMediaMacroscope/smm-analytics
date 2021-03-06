import csv
import os
import pandas as pd
import zipfile
import writeToS3 as s3


def organize_path_lambda(event):
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


def get_remote_input(remoteReadPath, filename, localReadPath):
    """
    download input file from s3 bucket to a local location, and then load
    it to a pandas dataframe
    :param remoteReadPath: remote path in s3 to store the data
    :param localReadPath: local location to store the data, usually in /tmp
    :return: df: dataframe that contains the complete input file
    """
    s3.downloadToDisk(filename, localReadPath, remoteReadPath)

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


def save_local_output(localSavePath, fname, output_data):
    with open(os.path.join(localSavePath, 'img', fname), 'wb') as f:
        f.write(output_data)


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            print(file)
            ziph.write(os.path.join(root, file), file)


def save_remote_output(localSavePath, remoteSavePath, fname):
    """

    :param localSavePath:
    :param remoteSavePath:
    :param fname:
    :param output_data:
    :return:
    """
    zipf = zipfile.ZipFile(os.path.join(localSavePath, fname), 'w',
                           zipfile.ZIP_DEFLATED)
    zipdir(os.path.join(localSavePath,'img'), zipf)
    zipf.close()

    s3.upload(localSavePath, remoteSavePath, fname)
    url = s3.generate_downloads(remoteSavePath, fname)

    return url
