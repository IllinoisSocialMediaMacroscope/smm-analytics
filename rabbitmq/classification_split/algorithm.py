import plot
from lambda_classification_split import Classification


def algorithm(df, params):
    """
    wrapper function to put each individual algorithm inside
    :param df: dataframe that contains all the input dataset
    :param params: algorithm specific parameters
    :return: a dictionary of { outputname: output content in memory }
    """
    output = {}

    CF = Classification(df, params['column'])

    output['uid'] = params['uid']

    training_set, testing_set = CF.split(int(params['ratio']))
    output['training'] = training_set
    output['testing'] = testing_set

    # plot
    labels = ['training set data points', 'unlabeled data points']
    values = [len(training_set), len(testing_set)]
    output['div'] = plot.plot_pie_chart(labels, values,
                                        title='breakdown of training vs testing size')

    return output
