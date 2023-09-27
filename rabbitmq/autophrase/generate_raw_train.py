import argparse
import csv

import pandas as pd

from writeToS3 import WriteToS3


def main(s3, remoteReadPath, column):
    filename = remoteReadPath.split('/')[-2] + '.csv'
    s3.downloadToDisk(filename=filename, localpath='data/', remotepath=remoteReadPath)

    Array = []
    try:
        with open('data/' + filename,'r',encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            try:
                for row in reader:
                    Array.append(row)
            except Exception as e:
                pass
    except:
        with open('data/' + filename,'r',encoding="ISO-8859-1", errors="ignore") as f:
            reader = csv.reader(f)
            try:
                for row in reader:
                    Array.append(row)
            except Exception as e:
                pass

    df = pd.DataFrame(Array[1:],columns=Array[0])
    df[df[column]!=''][column].dropna().astype('str').to_csv('data/raw_train.txt', index=False)

    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--remoteReadPath', required=True)
    parser.add_argument('--column', required=True)

    # user specified parameters
    parsed, unknown = parser.parse_known_args()
    for arg in unknown:
        if arg.startswith("--"):
            parser.add_argument(arg, required=False)

    params = vars(parser.parse_args())

    s3 = WriteToS3()
    main(s3, params['remoteReadPath'], params['column'])
