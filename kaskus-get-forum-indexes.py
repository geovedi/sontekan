# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import grequests
import plac
import itertools
import io
import regex as re

import logging
logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'
HEADERS = {'User-Agent': USER_AGENT}

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)

def main(output_prefix, base_url, start, end):
    for chunk in grouper(xrange(int(start), int(end)), 10):
        requests = (grequests.get(base_url + '/' + str(page_id), headers=HEADERS) for page_id in chunk)
        results = grequests.map(requests)
        for result in results:
            if not result.text:
                logging.error('Couldn\'t fetch {0}'.format(result.url))
            out_f = output_prefix + '/' + re.sub(r'\p{P}+', '_', result.url) + '.html'
            with io.open(out_f, 'w', encoding='utf-8') as out:
                out.write(result.text)
            logging.info('Saved {0}'.format(out_f))


if __name__ == '__main__':
    plac.call(main)
