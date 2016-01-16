# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import io
import itertools
import plac

def permutate(text):
    parts = text.split()
    pos = []
    for i, word in enumerate(parts):
        if '/' in word:
            pos.append(word.split('/'))
        else:
            pos.append([word])
    for combo in itertools.product(*pos):
        yield ' '.join(combo)


def main(input_fname, output_fname):
    with io.open(output_fname, 'w', encoding='utf-8') as out:
        for line in io.open(input_fname, 'r', encoding='utf-8'):
            for comb in permutate(line.strip()):
                out.write('{0}\n'.format(comb))

if __name__ == '__main__':
    plac.call(main)
