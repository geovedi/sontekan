# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

import plac
from random import shuffle
from urllib import unquote
from joblib import Parallel, delayed
from psutil import cpu_count
from numpydb import NumpyDB
from numpy import sqrt, ndarray
from timeout_decorator import timeout, TimeoutError

N_JOBS = cpu_count() - 1

def main(model_loc, lexicon, n_iters=10, n_jobs=N_JOBS):
    model = NumpyDB(model_loc)
    logging.info('Loaded model: {0}.'.format(model_loc))

    @timeout(30)
    def refit(words, verbose=False):
        wordset = set([word for word in words if isinstance(model[word], ndarray) and len(word) > 2])

        if len(wordset) <= 3:
            return

        # caching
        vectors = dict((word, model[word]) for word in wordset)

        for word in wordset:
            synonyms = [syn for syn in wordset if syn != word]
            if not synonyms:
                continue
            vector = len(synonyms) * vectors[word]
            for synonym in synonyms:
                vector += vectors[synonym]
            vector = vector / (2 * len(synonyms))
            vector /= sqrt((vector ** 2).sum(-1))
            vectors[word] = vector

        for word, vector in vectors.iteritems():
            if verbose:
                logging.info(('final', word, vector[:5]))
            model[word] = vector


    lines = open(lexicon).readlines()
    logging.info('Loaded lexicon: {0}.'.format(lexicon))

    for i in range(n_iters):
        logging.info('Iteration: {0}.'.format(i))
        shuffle(lines)
        c = 0
        for line in lines:
            cols = line.strip().split('\t')
            if len(cols) != 2: continue
            label, words = cols[0], cols[1]
            words = words.split(',')
            try:
                refit(words)
            except TimeoutError, e:
                logging.error((e, c, line))
            if c % 1000 == 0:
                logging.info('{0}: [{1}] {2}'.format(c, unquote(label), ', '.join(words[:10])))
            c += 1
    model.close()

if __name__ == '__main__':
    plac.call(main)
