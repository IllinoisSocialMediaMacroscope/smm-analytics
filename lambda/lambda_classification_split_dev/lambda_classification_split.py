import csv
import pandas
import random
import os
from plotly.offline import plot
import plotly.graph_objs as go
from os.path import join, dirname
import json
import re
import writeToS3 as s3


class Classification:

    def __init__(self, df, column):

        self.corpus = list(
            set(df[df[column] != ''][column].dropna().astype('str').tolist()))
        self.corpus = [re.sub(r"http\S+", "", text) for text in self.corpus]

    def split(self, ratio):
        training_set = [[item] for item in list(
            random.sample(self.corpus, int(len(self.corpus) * ratio / 100)))]
        training_set.insert(0, ['content', 'category'])

        testing_set = [[item] for item in self.corpus if
                       item not in training_set]
        testing_set.insert(0, ['content'])

        return training_set, testing_set
