# -*- coding: utf-8 -*-

import plac
import kenlm
import math
from collections import Counter

lm = kenlm.LanguageModel('corpus.ma.id.tokens.bin')

STOPWORDS = set(['bahwa', 'adalah', 'dan', 'dari', 'yang', 'ke'])

def main(arpa_file, output):
    scores = Counter()

    for line in open('corpus.ma.id.sents.pos.phrase.arpa'):
        if not '\t' in line:
            continue
        if '<unk>' in line or '<s>' in line or '</s>' in line:
            continue
        parts = line.strip().split('\t')
        phrase = parts[1]

        if (phrase.replace(' ', '').isdigit()
                    or set(phrase.split()) & STOPWORDS
                    or len(phrase) <= 2
                    or phrase[0].isdigit()
                    or phrase[1] == ' '):
            continue

        scores[phrase] = lm.score(phrase)

    with open(output, 'w') as out:
        for phrase, score in scores.most_common():
            out.write('{0}\t\t{1}\n'.format(round(math.exp(score), 5), phrase))


if __name__ == '__main__':
    plac.call(main)
