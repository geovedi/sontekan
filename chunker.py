# -*- coding: utf-8 -*-

import plac
import regex as re
import ftfy
from nltk import RegexpParser
from nltk.tag.util import str2tuple
from string import punctuation as punct

grammar = r"""
    NP:
        {<PNOUN|NOUN|NUM|\.>+<ADJ>?}
        
    VP:
        {<VERB>+}
"""

chunker = RegexpParser(grammar)


def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def main(corpus_file, output):
    with open(output, 'w') as out:
        for line in open(corpus_file):
            try:
                line = ftfy.fix_text(line.decode('utf-8'))
            except Exception, e:
                print e

            tokens = [str2tuple(tok) for tok in re.sub('\s+', ' ', line).split()]
            try:
                tree = chunker.parse(tokens)
            except Exception, e:
                print e
            for subtree in tree.subtrees(filter = lambda t: t.label() in ['NP', 'VP']):
                try:
                    text = [w.strip(punct) for (w, t) in subtree.leaves() if t != '.']
                    text = ' '.join(text).strip().lower()
                    if len(text) > 2 and not text.isdigit() and is_ascii(text):
                        out.write(text)
                        out.write('\n')
                except Exception, e:
                    print e

if __name__ == '__main__':
    plac.call(main)
