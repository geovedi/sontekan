# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import lxml.html
import plac
import json

import logging
logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

BASE_URL = 'http://www.kaskus.co.id'

def main(input_fname):
    html = lxml.html.parse(input_fname)
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

if __name__ == '__main__':
    plac.call(main)
