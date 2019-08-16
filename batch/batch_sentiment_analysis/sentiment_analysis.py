import pickle
from nltk import pos_tag, WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer, \
    allcap_differential, negated
from nltk.tokenize import word_tokenize
from nltk.corpus import sentiwordnet as swn, stopwords
import sentiment_analysis_debias as SA_debias


class Sentiment:

    def __init__(self, df, column):
        # user specify which column to; each row is a sentence, get a list of sentences
        self.sentences = df[df[column] != ''][column].dropna().astype(
            'str').tolist()

        # combine sentences into a document
        self.text = ''.join(self.sentences)

    def sentiment(self, algorithm='vader'):
        '''
        calculate sentence sentiment
        and store the list of scores in sentiment.csv
        '''

        if algorithm == 'vader':

            sid = SentimentIntensityAnalyzer()

            # sentence level
            sentiment_sentence = [
                ['sentence', 'negative', 'neutral', 'positive', 'compound']]
            for item in self.sentences:
                sent_scores = sid.polarity_scores(item)
                sentiment_sentence.append([item.encode('utf-8', 'ignore'),
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
            sentiment_sentence = [
                ['sentence', 'negative', 'neutral', 'positive']]
            for sent in self.sentences:
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

                    sentiment_sentence.append([sent.encode('utf-8', 'ignore'),
                                               self.average(neg_score),
                                               self.average(obj_score),
                                               self.average(pos_score)])

            # document level
            sentiment_doc = {'neg': self.average(doc_neg_score),
                             'neu': self.average(doc_obj_score),
                             'pos': self.average(doc_pos_score)}

        elif algorithm == 'debias':

            # load embeddings and model
            with open("sentiment_analysis_debias.pickle", "rb") as f:
                model = pickle.load(f)
            embeddings = SA_debias.load_embeddings('numberbatch-en-17.04b.txt')

            # sentence level
            sentiment_sentence = [['sentence', 'score']]
            doc_score = []
            for sent in self.sentences:

                # if valid
                score = SA_debias.text_to_sentiment(sent, embeddings, model)
                if score:
                    doc_score.append(score)
                    sentiment_sentence.append(
                        [sent.encode('utf-8', 'ignore'), round(score, 4)])
                else:
                    sentiment_sentence.append(
                        [sent.encode('utf-8', 'ignore'), 'NA'])

            # document level
            sentiment_doc = {'doc': self.average(doc_score)}

        else:
            sentiment_sentence = [[]]
            sentiment_doc = {}

        return sentiment_sentence, sentiment_doc

    def negated(self):
        '''
        find if a sentence has negation word
        store the True/false per sentence to negation.csv
        '''
        negation_result = [['sentence', 'hasNegation']]
        for item in self.sentences:
            negation_result.append(
                [item.encode('utf-8', 'ignore'), negated(item)])

        return negation_result

    def allcap(self):
        '''
        find if a sentence is composed of all capital letter
        store the True/False per sentence to allcap.csv
        '''
        allcap_result = [['sentence', 'ALL CAPITAL']]
        for item in self.sentences:
            allcap_result.append([item.encode('utf-8', 'ignore'),
                                  allcap_differential(item)])

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
