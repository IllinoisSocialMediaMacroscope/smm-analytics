import dataset
import plot
from lambda_classification_train import Classification


def algorithm(array, params):
    """
    wrapper function to put each individual algorithm inside
    :param array: array that contains all the input dataset
    :param params: algorithm specific parameters
    :return: a dictionary of { outputname: output content in memory }
    """

    output = {}

    CF = Classification(array)

    output['uid'] = params['uid']

    fold_scores, text_clf = CF.classify(params['model'])
    output['accuracy'] = fold_scores
    output['pipeline'] = text_clf

    labels = text_clf.classes_
    output['metrics'] = CF.calc_metrics(labels)

    # plot
    output['div_accuracy'] = plot.plot_bar_chart(fold_scores[0], fold_scores[1],
                                        title='10 fold cross validation accuracy score')

    return output


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
    for key, value in output.items():
        if key != 'uid':
            urls[key] = dataset.save_remote_output(path['localSavePath'],
                                                   path['remoteSavePath'],
                                                   key,
                                                   value)
        else:
            urls[key] = value

    return urls


if __name__ == "__main__":
    import csv

    Array = []
    with open('reddit-ml-multiclass.csv', 'r',encoding='ISO-8859-1') as f:
        reader = csv.reader(f)
        for row in reader:
            Array.append(row)

    # RandomForest
    params = {
        "uid":"11111111111111",
        "model":"AdaBoost"
    }
    output = algorithm(array=Array, params=params)
