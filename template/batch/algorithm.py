import plot
import pandas as pd

def algorithm(df, params):
    """
    wrapper function to put each individual algorithm inside
    :param df: dataframe that contains all the input dataset
    :param params: algorithm specific parameters
    :return: a dictionary of { outputname: output content in memory }
    """

    output = {}

    # PUT YOUR OWN IMPLEMENTATION HERE
    # STORE YOUR ANALYSIS OUTPUT IN OUTPUT

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

    }

    # execute your algorithm
    output = algorithm(df, params)

    # see if the outputs are what you desired
    print(output.keys())
