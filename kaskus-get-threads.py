# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import grequests
import plac
import itertools
import io
import regex as re
import lxml.html
import json

import logging
logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'
HEADERS = {'User-Agent': USER_AGENT}
BASE_URL = 'http://www.kaskus.co.id'


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)


def parse(result):
    if not result.text: return
    html = lxml.html.document_fromstring(result.text)
    for div_post in html.xpath('//div[@class="post"]'):
        data = {}
        link_thread = div_post.xpath('div[@class="post-title"]/a')[0]
        data['url'] = BASE_URL + link_thread.get('href')
        data['title'] = link_thread.text.strip()
        paginations = div_post.xpath('.//div[@class="pagination"]/ul/li/a')
        if paginations:
            data['last_page'] = int(paginations[-1].text)
        else:
            data['last_page'] = 1
        print json.dumps(data)


def main(forum_index, start, end):
    for chunk in grouper(xrange(int(start), int(end)), 100):
        requests = (grequests.get(forum_index + '/' + str(page_id), headers=HEADERS) for page_id in chunk)
        results = grequests.map(requests)
        map(parse, results)


if __name__ == '__main__':
    plac.call(main)
