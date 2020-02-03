from algorithm import algorithm
from dataset import Dataset


def lambda_handler(params, context):
    '''
    entrance to invoke AWS lambda,
    variable params contains parameters passed in
    '''

    if 'HOST_IP' in params.keys():
        HOST_IP = params['HOST_IP']
    else:
        HOST_IP = None

    if 'AWS_ACCESSKEY' in params.keys():
        AWS_ACCESSKEY = params['AWS_ACCESSKEY']
    else:
        AWS_ACCESSKEY = None

    if 'AWS_ACCESSKEYSECRET' in params.keys():
        AWS_ACCESSKEYSECRET = params['AWS_ACCESSKEYSECRET']
    else:
        AWS_ACCESSKEYSECRET = None

    if 'BUCKET_NAME' in params.keys():
        BUCKET_NAME = params['BUCKET_NAME']
    else:
        BUCKET_NAME = None

    d = Dataset(HOST_IP, AWS_ACCESSKEY, AWS_ACCESSKEYSECRET, BUCKET_NAME)
    urls = {}

    # arranging the paths
    path = d.dataset.organize_path_lambda(params)

    # save the config file
    urls['config'] = d.dataset.save_remote_output(path['localSavePath'],
                                                path['remoteSavePath'],
                                                'config',
                                                params)
    # prepare input dataset
    df = d.dataset.get_remote_input(path['remoteReadPath'],
                                  path['filename'],
                                  path['localReadPath'])

    # execute the algorithm
    output = algorithm(df, params)

    # upload object to s3 bucket and return the url
    for key, value in output.items():
        if key != 'uid':
            urls[key] = d.dataset.save_remote_output(path['localSavePath'],
                                                   path['remoteSavePath'],
                                                   key,
                                                   value)
        else:
            urls[key] = value

    return urls