

import numpy as np
from gensim import matutils
from embedding import Embedding

model_w2 = Embedding('model/id.generic.s300w2m1')
model_w10 = Embedding('model/id.generic.s300w10m1')


def most_similar(word, m1=None, m2=None, ctx_len=5, topn=10, max_vocab=10000):
    dists = np.dot(m1.vectors[:max_vocab], m1[word])
    best = np.argsort(dists)[::-1][:ctx_len + 1]
    ctx_words = [m1.metadata['index2word'][sim] for sim in best if float(dists[sim]) > 0.35][:ctx_len]

    ctx_mean = matutils.unitvec(np.array([m2[w] for w in ctx_words]).mean(axis=0)).astype(np.float32)
    dists = np.dot(m2.vectors[:max_vocab], ctx_mean)
    best = np.argsort(dists)[::-1][:topn + 1]
    result = [(m2.metadata['index2word'][sim], float(dists[sim]))
              for sim in best if m2.metadata['index2word'][sim] != word]
    return result[:topn]
