from algorithm import algorithm
from dataset import Dataset


def lambda_handler(params, context):
    '''
    entrance to invoke AWS lambda,
    variable params contains parameters passed in
    '''
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
    urls = {}

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

    return urls
