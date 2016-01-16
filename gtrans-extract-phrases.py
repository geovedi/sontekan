# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import plac
import json
import io
import logging
logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

def main(input_fname, source_output_fname, target_output_fname):
    try:
        doc = json.load(open(input_fname))
    except Exception, e:
        logging.error((input_fname, e))

    source_phrases, target_phrases = set(), set()
    # 0
    source_phrases.add(doc[0][0][1])
    target_phrases.add(doc[0][0][0])
    # 1
    if doc[1]:
        for i in doc[1]:
            target_phrases.update(set(i[1]))
            for j in i[2]:
                source_phrases.update(set(j[1]))
    # 11
    if len(doc) > 11:
        if doc[11]:
            for i in doc[11]:
                for j in i[1]:
                    source_phrases.update(set(j[0]))
    # 14
    if len(doc) > 14:
        if doc[14]:
            source_phrases.update(set(doc[14][0]))

    with io.open(source_output_fname, 'w', encoding='utf-8') as out:
        for phrase in source_phrases:
            out.write('{0}\n'.format(phrase))

    with io.open(target_output_fname, 'w', encoding='utf-8') as out:
        for phrase in target_phrases:
            out.write('{0}\n'.format(phrase))

if __name__ == '__main__':
    plac.call(main)
