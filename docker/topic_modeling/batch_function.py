import dataset
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
    for key, value in output.items():
        if key != 'uid':
            urls[key] = dataset.save_remote_output(path['localSavePath'],
                                                   path['remoteSavePath'],
                                                   key,
                                                   value)
        else:
            urls[key] = value

    # push notification email
    notification(toaddr=params['email'], case=3, filename=path['remoteSavePath'],
                 links=urls, sessionURL=params['sessionURL'])
