# -*- coding: utf-8 -*-

from __future__ import division
import plac
import kenlm
import math
import ftfy
from collections import Counter

lm = kenlm.LanguageModel('corpus.ma.id.tokens.bin')

STOPWORDS = set(['bahwa', 'adalah', 'dan', 'dari', 'yang', 'ke'])


# http://stackoverflow.com/a/7595897
def gen_ngrams(tokens, MIN_N, MAX_N):
    n_tokens = len(tokens)
    for i in xrange(n_tokens):
        for j in xrange(i+MIN_N, min(n_tokens, i+MAX_N)+1):
            yield tokens[i:j]

def main(corpus_file, output):
    counter = Counter()
    total = 0
    for line in open(corpus_file):
        try:
            line = ftfy.fix_text(line.decode('utf-8'))
        except Exception, e:
            print e
        tokens = line.strip().split()
        for ngram in gen_ngrams(tokens, 1, 2):
            phrase = ' '.join(ngram)
            if ngram[0].isdigit() or len(phrase) <= 2:
                continue
            counter[phrase] += 1
            total += 1
    with open(output, 'w') as out:
        for phrase, count in counter.most_common():
            out.write('{0}\t\t{1}\n'.format(count/total, phrase.encode('utf-8')))

if __name__ == '__main__':
    plac.call(main)
