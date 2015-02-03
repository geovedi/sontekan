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


class Model(Word2Vec):
    def refit(self, words, niters=5):
        wset = set([w for w in words if w in self.index2word])
        for i in range(niters):
            for w in wset:
                ns = [n for n in wset if n != w]
                if not ns:
                    continue
                v = len(ns) * self[w]
                for n in ns:
                    v += self[n]
                self.syn0[self.index2word.index(w)] = v / (2 * len(ns))


def main(model, lexicon):
    m = Model.load(model)

    def process(line):
        label, words = line.strip().split('\t')
        words = words.split(',')
        m.refit(words)
        logging.info('{0}: {1}'.format(unquote(label), ', '.join(words[:10])))

    Parallel(n_jobs=N_JOBS)(delayed(process)(line) for line in open(lexicon))
    m.save('{0}.fit'.format(model))


if __name__ == '__main__':
    plac.call(main)
