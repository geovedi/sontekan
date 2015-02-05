# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

import plac
from random import shuffle
from urllib import unquote
from gensim.models.word2vec import *
from joblib import Parallel, delayed
from psutil import cpu_count

N_JOBS = cpu_count() - 1


class Vector(object):
    def __init__(self, model, fvocab):
        self.word2vec = Word2Vec.load_word2vec_format(model, fvocab=fvocab, binary=False, norm_only=False)

    def refit(self, words, verbose=False):
        wordset = set([word for word in words 
                       if word in self.word2vec.index2word
                       and len(word) > 2])

        if len(wordset) <= 3:
            return

        for word in list(wordset):
            for wordsim, score in self.word2vec.most_similar(word, topn=5):
                if score >= 0.8:
                    wordset.add(wordsim)

        vectors = dict((word, self.word2vec[word]) for word in wordset)

        for word in wordset:
            synonyms = [syn for syn in wordset if syn != word]
            if not synonyms:
                continue
            vector = len(synonyms) * vectors[word]
            for synonym in synonyms:
                vector += vectors[synonym]
            vector = vector / (2 * len(synonyms))
            vectors[word] = vector

        for word, vector in vectors.iteritems():
            if verbose:
                logging.info(('final', word, vector[:5]))
            idxword = self.word2vec.index2word.index(word)
            self.word2vec.syn0[idxword] = vector



def main(model, fvocab, lexicon, n_iters=10, n_jobs=N_JOBS):
    model = Vector(model, fvocab)

    def process(line):
        label, words = line.strip().split('\t')
        words = words.split(',')
        model.refit(words)
        logging.info('{0}: {1}'.format(unquote(label), ', '.join(words[:10])))

    lines = open(lexicon).readlines()

    for i in range(n_iters):
        shuffle(lines)
        Parallel(n_jobs=n_jobs)(delayed(process)(line) for line in lines)
        model.save_word2vec_format('{0}-refit.{1}'.format(i, model), binary=False)


if __name__ == '__main__':
    plac.call(main)
