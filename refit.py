# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

import plac
import h5py
from random import shuffle
from urllib import unquote
from sqlitedict import SqliteDict


class Vector(object):
    def __init__(self, model_loc):
        self._h5 = h5py.File('{0}/wordvector.hdf5'.format(model_loc))
        self.vector = self._h5['wordvec']
        self.index = SqliteDict(key_type=unicode, value_type=int,
                                filename='{0}/index.sqlite3'.format(model_loc))


def main(model_loc, lexicon, n_iters=10):
    model = Vector(model_loc)

    # to speed up things, make sure the lexicon is already filtered
    def refit(i, line):
        label, words = line.strip().split('\t')
        words = words.split(',')
        #vectors = dict((word, model.vector[model.index[word]]) for word in words if word in model.index and len(word) > 2)
        #if len(vectors) < 3:
        #    return
        vectors = dict((word, model.vector[model.index[word]]) for word in words)
        for word in vectors.iterkeys():
            synonyms = [syn for syn in vectors.iterkeys() if syn != word]
            vector = len(synonyms) * vectors[word]
            for synonym in synonyms:
                vector += vectors[synonym]
            vector = vector / (2 * len(synonyms))
            vectors[word] = vector
        for word, vector in vectors.iteritems():
            model.vector[model.index[word]] = vector
        if i % 10000 == 0:
            logging.info('{0}: {1}'.format(unquote(label), ', '.join(words[:10])))

    lines = open(lexicon).readlines()
    logging.info('Processing lexicon {0} ({1} lines).'.format(lexicon, len(lines)))

    for i in range(n_iters):
        shuffle(lines)
        logging.info('Iteration: #{0}'.format(i))
        for i, line in enumerate(lines):
            refit(i, line)


if __name__ == '__main__':
    plac.call(main)
