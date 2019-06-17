import plot
import pandas as pd
import pickle
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english", ignore_stopwords=True)


class StemmedCountVectorizer(CountVectorizer):
    def build_analyzer(self):
        analyzer = super(StemmedCountVectorizer, self).build_analyzer()
        return lambda doc: ([stemmer.stem(w) for w in analyzer(doc)])


def algorithm(df, params):
    """
    wrapper function to put each individual algorithm inside
    :param df: dataframe that contains all the input dataset
    :param params: algorithm specific parameters
    :return: a dictionary of { outputname: output content in memory }
    """

    output = {}

    # load classification model
    with open(params['pipeline'] + ".pickle", 'rb') as f:
        text_clf = pickle.load(f)

    # load data
    data = df[df[params['column']] != ''][params['column']].dropna().astype('str').tolist()

    # predict using trained model
    predicted = text_clf.predict(data)
    result = [['text', 'class']]
    for i in range(len(data)):
        result.append([data[i], predicted[i]])
    output['predicted'] = result

    # plot percentage of class
    predicted_counts = Counter(predicted)
    labels = []
    values = []
    for key in predicted_counts.keys():
        labels.append("class: " + str(key))
        values.append(predicted_counts[key])
    output['div'] = plot.plot_pie_chart(labels, values, title="break down of the predicted class")

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
        "pipeline":"sutter_parenting_svm_stopwords_pipeline",
        "column": "text"
    }

    # execute your algorithm
    output = algorithm(df, params)

    # see if the outputs are what you desired
    print(output.keys())
    print(output['predicted'][:10])