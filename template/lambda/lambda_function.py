import dataset
import plot
from algorithm import algorithm

def lambda_handler(params, context):
    '''
    entrance to invoke AWS lambda,
    variable params contains parameters passed in
    '''
    urls = {}

    # arranging the paths
    path = dataset.organize_path_lambda(params)

    # save the config file
    urls['config'] = dataset.save_remote_output(path['localSavePath'],
                                                path['remoteSavePath'],
                                                'config',
                                                params)
    # prepare input dataset
    df = dataset.get_remote_input(path['remoteReadPath'],
                                  path['filename'],
                                  path['localReadPath'])

    # execute the algorithm
    output = algorithm(df, params)

    # upload object to s3 bucket and return the url
    # upload object to s3 bucket and return the url
    for key, value in output.items():
        if key != 'uuid':
            urls[key] = dataset.save_remote_output(path['localSavePath'],
                                                   path['remoteSavePath'],
                                                   key,
                                                   value)
        else:
            urls[key] = value

    return urls
