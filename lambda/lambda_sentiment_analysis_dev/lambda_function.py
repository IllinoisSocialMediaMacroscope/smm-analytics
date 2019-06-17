import dataset
import plot
from sentiment_analysis import Sentiment


def algorithm(df, params):
    """
    wrapper function to put each individual algorithm inside
    :param df: dataframe that contains all the input dataset
    :param params: algorithm specific parameters
    :return: a dictionary of { outputname: output content in memory }
    """

    output = {}

    # algorithm specific code
    # construct sentiment analysis
    SA = Sentiment(df, params['column'])

    sentiment_sentence, sentiment_doc = SA.sentiment(params['algorithm'])
    output['sentiment'] = sentiment_sentence
    output['doc'] = sentiment_doc

    if params['algorithm'] == 'vader':
        output['negation'] = SA.negated()
        output['allcap'] = SA.allcap()

    # plot
    labels = ['negative', 'neutral', 'positive']
    values = [sentiment_doc['neg'], sentiment_doc['neu'],
              sentiment_doc['pos']]
    output['div'] = plot.plot_pie_chart(labels, values,
                                        title='Sentiment of the dataset')

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
