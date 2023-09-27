from os import listdir
from os.path import isfile, join
import argparse
import json
import notification as n
from writeToS3 import WriteToS3

def main(s3, remoteSavePath):

    output = {}

    for file in listdir('results'):
        if isfile(join('results', file)):
            s3.upload('results', remoteSavePath, file)

            if file == 'config.json':
                output['config'] = s3.generate_downloads(remoteSavePath, file)
            elif file == 'div.html':
                output['visualization'] = s3.generate_downloads(remoteSavePath, file)
            elif file == 'AutoPhrase_multi-words.txt':
                output['multi-words'] = s3.generate_downloads(remoteSavePath, file)
            elif file == 'AutoPhrase_single-word.txt':
                output['single-word'] = s3.generate_downloads(remoteSavePath, file)
            elif file == 'AutoPhrase.txt':
                output['autophrase'] = s3.generate_downloads(remoteSavePath, file)
            elif file == 'segmentation.model':
                output['model'] = s3.generate_downloads(remoteSavePath, file)
            elif file == 'token_mapping.txt':
                output['token-mapping'] = s3.generate_downloads(remoteSavePath, file)
            else:
                output['misc'] = s3.generate_downloads(remoteSavePath, file)

    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--uid', required=True)
    parser.add_argument('--s3FolderName', required=True)
    parser.add_argument('--remoteReadPath', required=True)
    parser.add_argument('--column', required=True)
    parser.add_argument('--minSup', required=True)
    parser.add_argument('--email', required=True)
    parser.add_argument('--sessionURL', required=True)

    # user specified parameters
    parsed, unknown = parser.parse_known_args()
    for arg in unknown:
        if arg.startswith("--"):
            parser.add_argument(arg, required=False)

    params = vars(parser.parse_args())

    s3 = WriteToS3()

    # save parameters
    fname = 'config.json'
    with open(join('results', fname), "w") as f:
        json.dump(params, f)

    awsPath = params['s3FolderName'] + '/NLP/autophrase/'+ params['uid'] + '/'
    links = main(s3, awsPath)
    n.notification(params['email'], case=3, filename=awsPath, links=links,
                   sessionURL=params['sessionURL'])