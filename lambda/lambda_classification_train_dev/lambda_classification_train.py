from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn import metrics
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import cross_val_score
import numpy as np


class Classification:

    def __init__(self, array):

        self.data = []
        self.target = []

        for a in array[1:]:
            self.data.append(a[0])
            self.target.append(a[1])

    def classify(self, model):

        if model == 'NaiveBayes':
            text_clf = Pipeline(
                [('vect', CountVectorizer(stop_words='english')),
                 ('tfidf', TfidfTransformer()),
                 ('clf', MultinomialNB())])
            # 10 fold cross validation 
            self.predicted = cross_val_predict(text_clf, self.data,
                                               self.target, cv=10)
            # fit the model
            text_clf.fit(self.data, self.target)
        elif model == 'Perceptron':
            text_clf = Pipeline(
                [('vect', CountVectorizer(stop_words='english')),
                 ('tfidf', TfidfTransformer()),
                 ('clf', Perceptron())])
            # 10 fold cross validation 
            self.predicted = cross_val_predict(text_clf, self.data,
                                               self.target, cv=10)
            # fit the model
            text_clf.fit(self.data, self.target)
        elif model == 'SGD':
            text_clf = Pipeline(
                [('vect', CountVectorizer(stop_words='english')),
                 ('tfidf', TfidfTransformer()),
                 ('clf', SGDClassifier())])
            # 10 fold cross validation 
            self.predicted = cross_val_predict(text_clf, self.data,
                                               self.target, cv=10)
            # fit the model
            text_clf.fit(self.data, self.target)
        elif model == 'RandomForest':
            text_clf = Pipeline(
                [('vect', CountVectorizer(stop_words='english')),
                 ('tfidf', TfidfTransformer()),
                 ('clf', RandomForestClassifier(n_estimators=100))])
            # 10 fold cross validation 
            self.predicted = cross_val_predict(text_clf, self.data,
                                               self.target, cv=10)
            # fit the model
            text_clf.fit(self.data, self.target)
        elif model == 'KNN':
            text_clf = Pipeline(
                [('vect', CountVectorizer(stop_words='english')),
                 ('tfidf', TfidfTransformer()),
                 ('clf', KNeighborsClassifier(n_neighbors=10))])
            # 10 fold cross validation 
            self.predicted = cross_val_predict(text_clf, self.data,
                                               self.target, cv=10)
            # fit the model
            text_clf.fit(self.data, self.target)
        elif model == 'passiveAggressive':
            text_clf = Pipeline(
                [('vect', CountVectorizer(stop_words='english')),
                 ('tfidf', TfidfTransformer()),
                 ('clf', PassiveAggressiveClassifier(n_iter=50))])
            # 10 fold cross validation 
            self.predicted = cross_val_predict(text_clf, self.data,
                                               self.target, cv=10)
            # fit the model
            text_clf.fit(self.data, self.target)
        else:
            raise ValueError('Model not supported!')

        # get 10 fold cross validation accuracy score
        fold_scores = [['%.4f' % elem for elem in
                       cross_val_score(text_clf, self.data, self.target,
                                       cv=10)]]
        fold_scores.insert(0,
                           ['fold_1', 'fold_2', 'fold_3', 'fold_4', 'fold_5',
                            'fold_6', 'fold_7', 'fold_8', 'fold_9', 'fold_10'])

        return fold_scores, text_clf

    def calc_metrics(self, labels):
        metrics_output = []

        report = np.array(metrics.precision_recall_fscore_support(self.target,
                                                                  self.predicted,
                                                                  labels=labels)).T
        for i in range(len(report)):
            metrics_output.append(
                [labels[i], round(report[i][0], 4), round(report[i][1], 4),
                 round(report[i][2], 4), round(report[i][3], 4)])

        avg_report = list(metrics.precision_recall_fscore_support(self.target,
                                                                  self.predicted,
                                                                  average='weighted'))
        avg_report.insert(0, 'AVG')
        metrics_output.append(avg_report)

        return metrics_output
