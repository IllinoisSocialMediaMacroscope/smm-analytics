import pandas as pd
from run_ner import TwitterNER
from twokenize import tokenizeRawTweetText
import plot


def algorithm(df=None, params=None):
    """
    wrapper function to put each individual algorithm inside
    :param df: dataframe that contains all the input dataset
    :param params: algorithm specific parameters
    :return: a dictionary of { outputname: output content in memory }
    """

    output = {}

    # user specify which column to; each row is a sentence, get a list of sentences
    column = params['column']
    sentences = df[df[column] != ''][column].dropna().astype('str').tolist()

    entity_list = []
    entity_freq = {}
    entity_category = {}

    # extract entities in each sentence
    ner = TwitterNER()
    for sentence in sentences:
        tokens = tokenizeRawTweetText(sentence)
        raw_entities = ner.get_entities(tokens)

        entities = []
        for entry in raw_entities:
            # record entities
            entity = " ".join(tokens[entry[0]:entry[1]])
            category = entry[2]
            entities.append((entity, category))

            # record entity frequency
            if entity not in entity_freq.keys():
                entity_freq[entity] = 1
            else:
                entity_freq[entity] += 1

            # record category
            if category not in entity_category.keys():
                entity_category[category] = 1
            else:
                entity_category[category] += 1

        entity_list.append(entities)

    # extract entities in each sentence
    output['entity'] = entity_list

    # plot bar chart of most frequent entities
    output['freq'] = entity_freq

    output['div_freq'] = plot.plot_bar_chart(list(entity_freq.keys())[:30],
                                             list(entity_freq.values())[:30],
                                             "Top 30 Most Frequent Name Entities")

    # plot pie chart of entity categories
    output['div_category'] = plot.plot_pie_chart(list(entity_category.keys()),
                                                 list(entity_category.values()),
                                                 "Name Entity Category Breakdowns")

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
        "column": "text"
    }

    # execute your algorithm
    output = algorithm(df, params)

    # see if the outputs are what you desired
    print(output.keys())
    print(output['entity'][:5])
    print(output['freq'])
    print(output['div_freq'][:100])
    print(output['div_category'][:100])
