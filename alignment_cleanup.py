# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import regex as re
import plac
import io
from collections import Counter
from string import punctuation
import polyglot
from polyglot.base import Sequence
from polyglot.tokenize import WordTokenizer

import logging
logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)


def main(input_fname, output_fname, lang, to_lower=True):
    en_tokenizer = WordTokenizer(locale='en')
    fr_tokenizer = WordTokenizer(locale=lang)

    def tokenizer(text, tokenizer_fn):
        seq = Sequence(text.strip())
        return filter(lambda w: w != ' ', tokenizer_fn.transform(seq))

    logging.info((lang, "counting pairs"))
    counter = Counter()
    for line_no, line in enumerate(io.open(input_fname, 'r', encoding='utf-8')):
        if to_lower:
            line = line.lower()
        parts = line.rstrip().split(' ||| ')
        if len(parts) != 4: continue
        source_lang, source_text, target_text, count = parts
        source_tokens = tokenizer(source_text, en_tokenizer)
        target_tokens = tokenizer(target_text, fr_tokenizer)
        if len(source_tokens) > 3 or len(target_tokens) > 3: continue
        count = int(count)
        if count > 1:
            if (re.sub('\p{P}', '', source_text[0]) == ''
                or re.sub('\p{P}', '', target_text[0]) == ''
                or re.sub('\p{P}', '', source_text[-1]) == ''
                or re.sub('\p{P}', '', target_text[-1]) == ''):
                continue
            pair = ' ||| '.join([source_lang, 
                                 ' '.join(source_tokens),
                                 ' '.join(target_tokens)])
            counter[pair] += count
        if line_no % 100000 == 0:
            logging.info((lang, line_no))

    logging.info((lang, "writing pairs to {0}".format(output_fname)))
    with io.open(output_fname, 'w', encoding='utf-8') as out:
        for pair, count in counter.most_common():
            if count < 10:
                break
            out.write('{0} ||| {1}\n'.format(pair, count))


if __name__ == '__main__':
    plac.call(main)
