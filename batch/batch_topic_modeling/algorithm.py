import pandas as pd
from gensim_topic_modeling import Gensim_Topic_Modeling


def algorithm(df, params):
    """
    wrapper function to put each individual algorithm inside
    :param df: dataframe that contains all the input dataset
    :param params: algorithm specific parameters
    :return: a dictionary of { outputname: output content in memory }
    """

    output = {}

    gensim_tm = Gensim_Topic_Modeling(df, column=params["column"])
    data_lemmatized, id2word, corpus = gensim_tm.preprocessing()
    output['lemmatized'] = data_lemmatized

    lda_model = gensim_tm.build_lda_model(params['numTopics'], corpus, id2word)
    output['lda_model'] = lda_model

    metrics = gensim_tm.lda_model_metrics(
        lda_model, corpus, id2word, data_lemmatized)
    output['metrics'] = metrics

    html = gensim_tm.visualize_lda_model(lda_model, corpus, id2word)
    output['div'] = html

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
        "numTopics": 5,
    }

    # execute your algorithm
    output = algorithm(df, params)

    # see if the outputs are what you desired
    print(output['metrics'], output['div'])
