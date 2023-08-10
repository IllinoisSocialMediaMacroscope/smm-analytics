import random
import re


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
