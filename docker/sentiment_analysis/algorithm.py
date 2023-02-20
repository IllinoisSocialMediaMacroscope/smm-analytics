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
    if 'neg' in sentiment_doc.keys() and 'neu' in sentiment_doc.keys() and 'pos' in sentiment_doc.keys():
        labels = ['negative', 'neutral', 'positive']
        values = [sentiment_doc['neg'], sentiment_doc['neu'],
                  sentiment_doc['pos']]
        output['div'] = plot.plot_pie_chart(labels, values,
                                            title='Sentiment of the dataset')

    return output
