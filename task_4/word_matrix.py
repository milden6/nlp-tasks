from collections import defaultdict
from common_utils import sentence_preprocessing
from scipy import linalg
import numpy as np
import pandas as pd

#  co-occurrence matrix
def co_occurrence(sentences):
    def_dict = defaultdict(int)
    vocab_set = set()
    for text in sentences:

        text = sentence_preprocessing(text).split()

        for i in range(len(text)):
            token = text[i]
            vocab_set.add(token)  # add to vocab
            next_token = text[i + 1: i + 3]  # next token
            for t in next_token:
                key = tuple(sorted([t, token]))
                def_dict[key] += 1

    # formulate the dictionary into dataframe
    vocab = sorted(vocab_set)  # sort vocab

    data_frame = pd.DataFrame(data=np.zeros((len(vocab), len(vocab)), dtype=np.int16),
                              index=vocab,
                              columns=vocab)

    for key, value in def_dict.items():
        data_frame.at[key[0], key[1]] = value
        data_frame.at[key[1], key[0]] = value
    return data_frame

#  Positive Pointwise Mutual Information
def ppmi(data_frame):
    col_totals = data_frame.sum(axis=0)
    total = col_totals.sum()
    row_totals = data_frame.sum(axis=1)
    expected = np.outer(row_totals, col_totals) / total
    data_frame = data_frame / expected

    with np.errstate(divide='ignore'):
        data_frame = np.log(data_frame)
    data_frame[np.isinf(data_frame)] = 0.0
    data_frame[data_frame < 0] = 0.0
    return data_frame


#  measure of similarity between two non-zero vectors by cos
def cosine_similarity(a, b):
    dot = np.dot(a, b)
    norma = np.linalg.norm(a)
    normb = np.linalg.norm(b)
    cosine = dot / (norma * normb)
    return cosine

# measure of similarity between two non-zero vectors by scalar
def scalar(a, b):
    length = min(a.shape[0], b.shape[0])
    scalar = 0
    for i in range(0, length):
        scalar = scalar + a[i]*b[i]
    return scalar


def lsa(matrix):
    # singular value decomposition
    # u - unitary matrix having left singular vectors as columns
    # sigma - the singular values, sorted in non-increasing order
    # vt - unitary matrix having right singular vectors as rows
    u, sigma, vt = linalg.svd(matrix)

    # construct the sigma matrix in SVD from singular values and size M, N
    # and transform
    transformed_matrix = np.dot(np.dot(u, linalg.diagsvd(sigma, len(matrix), len(vt))), vt)

    col = matrix.keys()
    data_frame = pd.DataFrame(data=transformed_matrix, columns=col, index=col )

    return data_frame
