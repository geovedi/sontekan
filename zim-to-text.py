# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import plac
import io
import json
import html2text
import ftfy

from iiab.zimpy import ZimFile

import logging
logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

text_maker = html2text.HTML2Text()
text_maker.unicode_snob = True
text_maker.ignore_images = True
text_maker.ignore_links = True
text_maker.ignore_emphasis = True
text_maker.body_width = 0

def cleanup(text):
    text = text.replace('\-', '-')
    return text

def main(zim_fname, output_fname):
    z = ZimFile(zim_fname)
    with io.open(output_fname, 'w', encoding='utf-8') as out:
        for entry_no, entry in enumerate(z.articles()):
            title = ftfy.fix_text(entry['title'])
            if entry['namespace'] == 'A' and not entry.get('redirectIndex'):
                article, _, _ = z.get_article_by_index(entry['index'],
                                                       follow_redirect=False)
                text = text_maker.handle(article.decode('utf-8'))
                data = {'title': title, 'text': cleanup(text)}
                out.write(json.dumps(data).decode('utf-8'))
                out.write('\n')
                logging.info((entry['index'], title))

if __name__ == '__main__':
    plac.call(main)
