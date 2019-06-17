import plot
import pandas as pd
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
        "process": "stemming",
        "tagger":"posTag"
    }

    # execute your algorithm
    output = algorithm(df, params)

    # see if the outputs are what you desired
    print(output.keys())
    print(output['phrases'][:5])
    print(output['filtered'][:5])
    print(output['processed'][:5])
    print(output['tagged'][:5])
    print(output['most_common'][:5])
    print(output['div'][:100])
