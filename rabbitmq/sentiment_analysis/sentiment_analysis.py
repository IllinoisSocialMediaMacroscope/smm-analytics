import itertools

from nltk import pos_tag, WordNetLemmatizer
from nltk.corpus import sentiwordnet as swn, stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer, \
    allcap_differential, negated
from nltk.tokenize import word_tokenize


class Sentiment:

    def __init__(self, df, column):
        # user specify which column to; each row is a sentence, get a list of sentences
        self.id_column = "id"
        if 'id_str' in df.columns:
            self.id_column = 'id_str'
            df_new = df[df[column] != ''][[self.id_column, column]].dropna()
            self.sentences = df_new[column].astype('str').tolist()
            self.id = df_new[self.id_column].astype('str').tolist()
        elif 'id' in df.columns:
            self.id_column = 'id'
            df_new = df[df[column] != ''][[self.id_column, column]].dropna()
            self.sentences = df_new[column].astype('str').tolist()
            self.id = df_new[self.id_column].astype('str').tolist()
        elif 'comment_id' in df.columns:
            self.id_column = 'comment_id'
            df_new = df[df[column] != ''][[self.id_column, column]].dropna()
            self.sentences = df_new[column].astype('str').tolist()
            self.id = df_new[self.id_column].astype('str').tolist()
        elif '_source.id_str':
            self.id_column = '_source.id_str'
            df_new = df[df[column] != ''][[self.id_column, column]].dropna()
            self.sentences = df_new[column].astype('str').tolist()
            self.id = df_new[self.id_column].astype('str').tolist()
        elif '_source.id':
            self.id_column = '_source.id_str'
            df_new = df[df[column] != ''][[self.id_column, column]].dropna()
            self.sentences = df_new[column].astype('str').tolist()
            self.id = df_new[self.id_column].astype('str').tolist()
        else:
            self.sentences = df[df[column] != ''][column].dropna().astype(
                'str').tolist()
            self.id = []

        # combine sentences into a document
        self.text = ''.join(self.sentences)

    def sentiment(self, algorithm='vader'):
        '''
        calculate sentence sentiment
        and store the list of scores in sentiment.csv
        '''

        sid = SentimentIntensityAnalyzer()

        sentiment_sentence = [
            [self.id_column, 'sentence', 'negative', 'neutral', 'positive', 'compound']]
        sentiment_doc = {}

        if algorithm == 'vader':
            # sentence level
            for sent_id, sent in itertools.zip_longest(self.id, self.sentences):
                sent_scores = sid.polarity_scores(sent)
                sentiment_sentence.append([sent_id,
                                           sent.encode('utf-8', 'ignore'),
                                           sent_scores['neg'],
                                           sent_scores['neu'],
                                           sent_scores['pos'],
                                           sent_scores['compound']])

            # document level
            sentiment_doc = sid.polarity_scores(self.text)

        elif algorithm == 'sentiWordNet':
            doc_pos_score = []
            doc_neg_score = []
            doc_obj_score = []

            # sentence level
            for sent_id, sent in itertools.zip_longest(self.id, self.sentences):
                tokens = word_tokenize(sent)

                filtered_tokens = [word.lower() for word in tokens
                                   if (word.isalpha() == True
                                       and word.lower()
                                       not in stopwords.words('english'))]

                wnl = WordNetLemmatizer()
                processed_tokens = [wnl.lemmatize(word) for word in
                                    filtered_tokens]
                tagged = pos_tag(processed_tokens)

                # convert pos tag to sentiwordnet tag
                pos_score = []
                neg_score = []
                obj_score = []
                for tag in tagged:
                    word = tag[0].lower()
                    pos = self.pos_short(tag[1])

                    # calculate scores
                    senti_synset = list(swn.senti_synsets(word, pos))

                    if len(senti_synset) > 0:
                        # use the most common meaning, 0
                        pos_score.append(senti_synset[0].pos_score())
                        neg_score.append(senti_synset[0].neg_score())
                        obj_score.append(senti_synset[0].obj_score())
                # if valid
                if pos_score != [] or neg_score != [] or obj_score != []:
                    doc_pos_score.append(self.average(pos_score))
                    doc_neg_score.append(self.average(neg_score))
                    doc_obj_score.append(self.average(obj_score))

                    sentiment_sentence.append([sent_id,
                                               sent.encode('utf-8', 'ignore'),
                                               self.average(neg_score),
                                               self.average(obj_score),
                                               self.average(pos_score),
                                               'NA'])

            # document level
            sentiment_doc = {'neg': self.average(doc_neg_score),
                             'neu': self.average(doc_obj_score),
                             'pos': self.average(doc_pos_score)}

        return sentiment_sentence, sentiment_doc

    def negated(self):
        '''
        find if a sentence has negation word
        store the True/false per sentence to negation.csv
        '''
        negation_result = [[self.id_column, 'sentence', 'hasNegation']]
        for sent_id, sent in itertools.zip_longest(self.id, self.sentences):
            negation_result.append(
                [sent_id, sent.encode('utf-8', 'ignore'), negated(sent)])

        return negation_result

    def allcap(self):
        '''
        find if a sentence is composed of all capital letter
        store the True/False per sentence to allcap.csv
        '''
        allcap_result = [[self.id_column,'sentence', 'ALL CAPITAL']]
        for sent_id, sent in itertools.zip_longest(self.id, self.sentences):
            allcap_result.append([sent_id, sent.encode('utf-8', 'ignore'),
                                  allcap_differential(sent)])

        return allcap_result

    ##########################################################################
    def average(self, score_list):
        """Get arithmetic average of scores."""
        if (score_list):
            # round to 4 decimals
            return round(sum(score_list) / float(len(score_list)), 4)

    def pos_short(self, pos):
        """Convert NLTK POS tags to SWN's POS tags."""
        if pos in set(['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']):
            return 'v'
        elif pos in set(['JJ', 'JJR', 'JJS']):
            return 'a'
        elif pos in set(['RB', 'RBR', 'RBS']):
            return 'r'
        elif pos in set(['NNS', 'NN', 'NNP', 'NNPS']):
            return 'n'
        else:
            return 'a'
