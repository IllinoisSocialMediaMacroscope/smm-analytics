import pandas as pd
import re
import numpy as np


def load_embeddings(filename):
    """
    Load a DataFrame from the generalized text format used by word2vec, GloVe,
    fastText, and ConceptNet Numberbatch. The main point where they differ is
    whether there is an initial line with the dimensions of the matrix.
    """
    labels = []
    rows = []
    with open(filename, encoding='utf-8') as infile:
        for i, line in enumerate(infile):
            items = line.rstrip().split(' ')
            if len(items) == 2:
                # This is a header row giving the shape of the matrix
                continue
            labels.append(items[0])
            values = np.array([float(x) for x in items[1:]], 'f')
            rows.append(values)

    arr = np.vstack(rows)
    return pd.DataFrame(arr, index=labels, dtype='f')


def text_to_sentiment(text, embeddings, model):
    # tokenize the sentence
    TOKEN_RE = re.compile(r"\w.*?\b")
    tokens = [token.casefold() for token in TOKEN_RE.findall(text)]

    # calculate the score
    try:
        vecs = embeddings.loc[tokens].dropna()
        predictions = model.predict_log_proba(vecs)
        log_odds = predictions[:, 1] - predictions[:, 0]
        sentiments = pd.DataFrame({'sentiment': log_odds}, index=vecs.index)

        return sentiments['sentiment'].mean()

    except:
        return None
