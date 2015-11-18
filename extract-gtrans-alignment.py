# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import regex as re
import plac
import io
import ftfy
import fileinput
import polyglot
from polyglot.base import Sequence
from polyglot.tokenize import WordTokenizer
from cachetools import cached, LRUCache
from smart_open import smart_open

import logging
logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)


PUNCTSYM = re.compile(r'^[\p{P}\p{S}]+$')
LIKENUM = re.compile(r'^[\p{N},\.-]+$')
LIKEUNIT = re.compile(r'^[\p{N},\.-]+(\w+)$')
CONTRACTION1 = re.compile(r"(\w+)'(s|m|re|ve|d|ll)$")
CONTRACTION2 = re.compile(r"(\w+)n't$")

cache = LRUCache(maxsize=100000)

@cached(cache)
def tokenizer(text, tokenizer_fn, to_lower=False):
    text = ftfy.fix_text(text)
    if to_lower:
        text = text.lower()
    try:
        seq = Sequence(text.strip())
    except ValueError:
        return
    tokens = tokenizer_fn.transform(seq)
    new_tokens = []
    for token in tokens:
        if token.strip() == '':
            continue
        elif PUNCTSYM.search(token):
            token = '$'
        elif LIKENUM.search(token):
            token = '0'
        elif LIKEUNIT.search(token):
            token = LIKEUNIT.sub(r'0 \1', token)
        elif token == "can't":
            token = 'can not'
        elif CONTRACTION1.search(token):
            token = CONTRACTION1.sub(r"\1 '\2", token)
        elif CONTRACTION2.search(token):
            token = CONTRACTION2.sub(r"\1 n't", token)
        new_tokens.append(token)
    if new_tokens:
        return ' '.join(new_tokens).strip()
    return


def main(input_fname, lang, to_lower=True):
    en_tokenizer = WordTokenizer(locale='en')
    fr_tokenizer = WordTokenizer(locale=lang)

    for line_no, line in enumerate(smart_open(input_fname)):
        data = json.loads(line)
        en_text, pairs = data[0][0][1], data[5]
        if not isinstance(pairs, list):
            logging.error((input_fname, 'not list', pairs))
            continue
        for source, _, targets, _, _, _, _ in pairs:
            if not isinstance(targets, list):
                logging.error((input_fname, 'not list', targets))
                continue
            for target in targets:
                if source in en_text:
                    count = int(target[1]) or 1
                    source = tokenizer(source, en_tokenizer, to_lower)
                    target = tokenizer(target[0], fr_tokenizer, to_lower)
                    if source and target:
                        print('{0} ||| {1} ||| {2}'.format(source, target, count).encode('utf-8'))
        if line_no % 10000 == 0:
            logging.info((input_fname, line_no))

if __name__ == '__main__':
    plac.call(main)
