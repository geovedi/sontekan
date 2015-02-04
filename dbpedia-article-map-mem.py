# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


import pickle
import ujson as json
import regex as re
from urllib import unquote
from collections import defaultdict
from unidecode import unidecode
from rdflib.plugins.parsers.ntriples import NTriplesParser, Sink
from joblib import Parallel, delayed
from psutil import cpu_count

N_JOBS = 10


def norm(text):
    return '_'.join(re.sub(r'[\p{P}\p{S}]+', ' ',
                    re.sub(r'\d+', '0', unidecode(text).lower())).split())


def norm_(text):
    text = unquote(text)
    text = text.replace('http://dbpedia.org/resource/', '')
    text = text.replace('Category:', '')
    text = re.sub(r' \(.*?\)$', '', text)
    return norm(text)


class Label(Sink):
    def __init__(self):
        self.store = defaultdict(set)

    def triple(self, s, p, o):
        k = s.encode('utf-8')
        self.store[k].add(norm_(o).encode('utf-8'))
        if ', ' in o:
            for v in o.split(', '):
                self.store[k].add(norm_(v).encode('utf-8'))
        self.store[k].add(norm(o).encode('utf-8'))
        logging.info('labels: {0} => {1}'.format(unquote(k), list(self.store[k])))


class Category(Sink):
    def __init__(self, labels):
        self.store = defaultdict(set)
        self.labels = labels
        if not self.labels:
            raise Exception('Labels not set.')

    def triple(self, s, p, o):
        k = o.encode('utf-8')
        s = s.encode('utf-8')
        for v in self.labels.get(s, default=set()):
            self.store[k].add(v)
        logging.info('categories: {0} => {1}'.format(unquote(k), list(self.store.get(k))[:5]))


if __name__ == '__main__':

    labels = NTriplesParser(sink=Label())

    def process_labels(line):
        labels.parsestring(line)

    for filename in ['./labels_en.nt',
                     './labels_en_uris_id.nt',
                     './category_labels_en.nt',
                     './category_labels_en_uris_id.nt']:
        logging.info('labels: processing: {0}'.format(filename))
        Parallel(n_jobs=N_JOBS)(delayed(process_labels)(line) for line in open(filename))

    pickle.dump(labels.sink.store, open('labels.p', 'wb'))

    categories = NTriplesParser(sink=Category(labels=labels.sink.store))

    def process_categories(line):
        categories.parsestring(line)

    for filename in ['./article_categories_en.nt',
                     './article_categories_en_uris_id.nt']:
        logging.info('categories: processing: {0}'.format(filename))
        Parallel(n_jobs=N_JOBS)(delayed(process_categories)(line) for line in open(filename))

    pickle.dump(categories.sink.store, open('categories.p', 'wb'))

    with open('categories.txt', 'w') as out:
        for k, v in categories.sink.db:
            v = json.loads(v)
            out.write('{0}\t{1}\n'.format(unquote(k), ','.join(v)))
            logging.info('map: {0}\t{1}'.format(unquote(k), ','.join(v)))

