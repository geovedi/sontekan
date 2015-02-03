# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

from urllib import unquote
from gensim.models.word2vec import *
from joblib import Parallel, delayed
from psutil import cpu_count
import plac

N_JOBS = cpu_count() - 1


class Vector(object):
    def __init__(self, model):
        self.word2vec = Word2Vec.load(model)

    def refit(self, words, niters=5, verbose=False):
        wordlist = set([word for word in words if word in self.word2vec.index2word])
        for i in range(niters):
            for word in wordlist:
                if verbose:
                    logging.info((i, word, self.word2vec[word][:5]))
                synonyms = [syn for syn in wordlist if syn != word]
                if not synonyms:
                    continue
                vector = len(synonyms) * self.word2vec[word]
                for synonym in synonyms:
                    vector += self.word2vec[synonym]
                idxword = self.word2vec.index2word.index(word)
                self.word2vec.syn0[idxword] = vector / (2 * len(synonyms))
                if verbose:
                    logging.info((i, word, self.word2vec[w][:5]))


def main(model, lexicon, n_jobs=N_JOBS):
    model = Vector(model)

    def process(line):
        label, words = line.strip().split('\t')
        words = words.split(',')
        model.refit(words)
        logging.info('{0}: {1}'.format(unquote(label), ', '.join(words[:10])))

    Parallel(n_jobs=n_jobs)(delayed(process)(line) for line in open(lexicon))
    model.save('{0}.fit'.format(model))


if __name__ == '__main__':
    plac.call(main)
