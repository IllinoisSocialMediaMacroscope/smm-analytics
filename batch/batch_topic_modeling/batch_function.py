from dataset import Dataset
import argparse
from notification import notification
from algorithm import algorithm

if __name__ == '__main__':

    # entrance to invoke Batch
    urls = {}

    # default parameters
    parser = argparse.ArgumentParser(description="processing...")
    parser.add_argument('--remoteReadPath', required=True)
    parser.add_argument('--column', required=True)
    parser.add_argument('--s3FolderName', required=True)
    parser.add_argument('--uid', required=True)
    parser.add_argument('--resultPath', required=True)
    parser.add_argument('--email', required=True)
    parser.add_argument('--sessionURL', required=True)

    # user specified parameters
    parsed, unknown = parser.parse_known_args()
    for arg in unknown:
        if arg.startswith("--"):
            parser.add_argument(arg, required=False)

    params = vars(parser.parse_args())

    if 'MINIO_URL' in params.keys():
        MINIO_URL = params['MINIO_URL']
        params.pop('MINIO_URL', None)
    else:
        MINIO_URL = None

    if 'AWS_ACCESSKEY' in params.keys():
        AWS_ACCESSKEY = params['AWS_ACCESSKEY']
        params.pop('AWS_ACCESSKEY', None)
    else:
        AWS_ACCESSKEY = None

    if 'AWS_ACCESSKEYSECRET' in params.keys():
        AWS_ACCESSKEYSECRET = params['AWS_ACCESSKEYSECRET']
        params.pop('AWS_ACCESSKEYSECRET', None)
    else:
        AWS_ACCESSKEYSECRET = None

    if 'BUCKET_NAME' in params.keys():
        BUCKET_NAME = params['BUCKET_NAME']
        params.pop('BUCKET_NAME', None)
    else:
        BUCKET_NAME = None

    d = Dataset(MINIO_URL, AWS_ACCESSKEY, AWS_ACCESSKEYSECRET, BUCKET_NAME)

    # arranging the paths
    path = d.organize_path_lambda(params)

    # save the config file
    urls['config'] = d.save_remote_output(path['localSavePath'],
                                                path['remoteSavePath'],
                                                'config',
                                                params)

    # prepare input dataset
    df = d.get_remote_input(path['remoteReadPath'],
                                  path['filename'],
                                  path['localReadPath'])

    # execute the algorithm
    output = algorithm(df, params)

    # upload object to s3 bucket and return the url
    for key, value in output.items():
        if key != 'uid':
            urls[key] = d.save_remote_output(path['localSavePath'],
                                                   path['remoteSavePath'],
                                                   key,
                                                   value)
        else:
            urls[key] = value

    # push notification email
    notification(toaddr=params['email'], case=3, filename=path['remoteSavePath'],
                 links=urls, sessionURL=params['sessionURL'])
