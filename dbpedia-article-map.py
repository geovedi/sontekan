# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


import plyvel
import pickle
import ujson as json
import regex as re
from urllib import unquote
from collections import defaultdict
from unidecode import unidecode
from rdflib.plugins.parsers.ntriples import NTriplesParser, Sink


def norm(text):
    return '_'.join(re.sub(r'[\p{P}\p{S}]+', ' ',
                    re.sub(r'\d+', '0', unidecode(text).lower())).split())

def norm_(text):
    text = text.replace('http://dbpedia.org/resource/', '')
    text = text.replace('Category:', '')
    return norm(text)


class Label(Sink):
    def __init__(self, loc):
        self.db = plyvel.DB(loc, create_if_missing=True)

    def triple(self, s, p, o):
        k = s.encode('utf-8')
        v = norm(o).encode('utf-8')
        v_ = norm_(o).encode('utf-8')
        # store prop:name, also prop:label
        data = self.db.get(k, default=set())
        if data:
            data = set(json.loads(data))
        data.add(v)
        data.add(v_)
        self.db.put(k, json.dumps(list(data)))
        logging.info('labels: {0} => {1}'.format(k, data))


class Category(Sink):
    def __init__(self, loc, wordset=set(), labels=None):
        self.db = plyvel.DB(loc, create_if_missing=True)
        self.wordset = wordset
        self.labels = labels

    def triple(self, s, p, o):
        k = o.encode('utf-8')
        s = s.encode('utf-8')

        if self.labels:
            v = self.labels.get(s, default=set())

        if v:
            v = set(json.loads(v))

        data = self.db.get(k, default=set())
        if data:
            data = set(json.loads(data))

        for w in v:
            if w in self.wordset:
                data.add(w)

        if data:
            self.db.put(k, json.dumps(list(data)))
            logging.info('categories: {0} => {1}'.format(k, v))


if __name__ == '__main__':

    wordset = set(pickle.load(open('./wordset.p')))
    labels = NTriplesParser(sink=Label('./labels'))
    categories = NTriplesParser(sink=Category('./categories', 
                                wordset=wordset, labels=labels.sink.db))


    for filename in ['./labels_en.nt',
                     './labels_en_uris_id.nt',
                     './category_labels_en.nt',
                     './category_labels_en_uris_id.nt']:
        logging.info('labels: processing: {0}'.format(filename))
        for line in open(filename):
            labels.parsestring(line)

    for filename in ['./article_categories_en.nt',
                     './article_categories_en_uris_id.nt']:
        logging.info('categories: processing: {0}'.format(filename))
        for line in open(filename):
            categories.parsestring(line)

    with open('categories.txt', 'w') as out:
        for k, v in categories.sink.db:
            v = json.loads(v)
            if len(v) >= 3 and not 'establishments' in k \
                and not k.endswith('births') \
                and not k.endswith('deaths'):
                out.write('{0}\t{1}\n'.format(unquote(k), ','.join(v)))

    labels.sink.db.close()
    categories.sink.db.close()
