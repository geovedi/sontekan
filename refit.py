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

def main(model, lexicon):
    m = Word2Vec.load(model)

    def fit(words, niters=5):
        wset = set([w for w in words if w in m.index2word])
        wvec = dict((w, m[w]) for w in wset)
        for i in range(niters):
            for w in wset:
                ns = wset - set([w])
                nns = len(ns)
                if nns == 0:
                    continue
                vec = nns * wvec[w]
                for nword in ns:
                    vec += m[nword]
                m.syn0[m.index2word.index(w)] = vec / (2 * nns)

    def process(line):
        label, words = line.strip().split('\t')
        words = words.split(',')
        fit(words)
        logging.info('{0}: {1}'.format(unquote(label), ', '.join(words[:10])))

    Parallel(n_jobs=N_JOBS)(delayed(process)(line) for line in open(lexicon))
    m.save('{0}.fit'.format(model))

if __name__ == '__main__':
    plac.call(main)
