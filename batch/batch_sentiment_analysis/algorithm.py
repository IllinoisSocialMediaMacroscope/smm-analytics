import plot
import pandas as pd
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
    if 'neg' in sentiment_doc.keys() \
            and 'neu' in sentiment_doc.keys() \
            and 'pos' in sentiment_doc.keys():
        labels = ['negative', 'neutral', 'positive']
        values = [sentiment_doc['neg'], sentiment_doc['neu'],
                  sentiment_doc['pos']]
        output['div'] = plot.plot_pie_chart(labels, values,
                                            title='Sentiment of the dataset')

    return output


if __name__ == '__main__':
    """ 
    help user with no access to AWS test their model
    to test just run algorithm.py:
    python3 algorithm.py
    """

    # download our example dataset and place it under the same directory of this script
    df = pd.read_csv('example_dataset.csv')

    # add your parameters needed by the analysis
    params = {
        "column": "text",
        "algorithm": "debias"
    }

    # execute your algorithm
    output = algorithm(df, params)

    # see if the outputs are what you desired
    print(output.keys())
    print(output['sentiment'][:5])
    print(output['doc'])
    # print(output['negation'][:5])
    # print(output['allcap'][:5])
    # print(output['div'][:100])
