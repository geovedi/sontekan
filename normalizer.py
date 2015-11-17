# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import regex as re
import fileinput
import ftfy

PUNCTSYM = re.compile(r'^[\p{P}\p{S}]+$')
LIKENUM = re.compile(r'^[\p{N},\.-]+$')
LIKEUNIT = re.compile(r'^[\p{N},\.-]+(\w+)$')
CONTRACTION1 = re.compile(r"(\w+)'(s|m|re|ve|d|ll)$")
CONTRACTION2 = re.compile(r"(\w+)n't$")

def main():
    for line in fileinput.input():
        line = ftfy.fix_text(line.decode('utf-8'))
        tokens = line.split()
        new_tokens = []
        for token in tokens:
            if PUNCTSYM.search(token):
                token = '$'
            elif LIKENUM.search(token):
                token = '0'
            elif LIKEUNIT.search(token):
                token = LIKEUNIT.sub(r'0\t\1', token)
            elif token == "can't":
                token = 'can\tnot'
            elif CONTRACTION1.search(token):
                token = CONTRACTION1.sub(r"\1\t'\2", token)
            elif CONTRACTION2.search(token):
                token = CONTRACTION2.sub(r"\1\tn't", token)
            new_tokens.append(token)
        line = '\t'.join(new_tokens)
        print(line.encode('utf-8'))

if __name__ == '__main__':
    main()
