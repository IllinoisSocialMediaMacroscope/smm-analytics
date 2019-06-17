import dataset
import plot
from preprocessing import Preprocess


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
    PP = Preprocess(df, params['column'])

    output['phrases'] = PP.get_phrases()
    output['filtered'] = filtered_tokens = PP.get_words()
    output['processed'] = processed_tokens = PP.stem_lematize(
        params['process'], filtered_tokens)
    output['tagged'] = PP.tagging(params['tagger'], processed_tokens)
    filtered_most_common, processed_most_common = PP.most_frequent(
        filtered_tokens, processed_tokens)
    output['most_common'] = processed_most_common

    # plot
    index = []
    counts = []
    for common in processed_most_common[1:51]:
        index.append(common[0])
        counts.append(common[1])
    title = 'Top 50 frequent words (' + params['process'] + ')'
    output['div'] = plot.plot_bar_chart(index, counts, title)

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
