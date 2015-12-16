
import plac
import json
import arrow
import lxml.html
import regex as re
from lxml.cssselect import CSSSelector


post_selector = CSSSelector('div.post')

def get_thread_id(html):
    try:
        return int(re.findall('/thread/(\d+)\/',
                   html.xpath('//link[@rel="canonical"]')[0].get('href'))[0])
    except:
        return

def process_post(post):
    post_data = {}
    try:
        post_data['user_id'] = int(post.xpath('./div[@class="poster"]/div[@class="left"]/a')[0].get('href').split('=')[1])
    except:
        pass
    try:
        post_data['user_name'] = post.xpath('./div[@class="poster"]/div[@class="left"]/a')[0].text
    except:
        pass
    try:
        post_data['post_date'] = arrow.get(post.xpath('./div[@class="poster"]/div[@class="left"]')[0].xpath('text()')[1].strip('\n\t- '), 'DD/MM/YYYY HH:mm A').isoformat()
    except:
        pass
    try:
        post_data['post_seq'] = int(post.xpath('./div[@class="poster"]/div[@class="right"]')[0].get('id'))
    except:
        pass
    try:
        post_data['post_text'] = lxml.etree.tostring(post.xpath('./div[@class="pagetext"]')[0], pretty_print=True).strip()
    except:
        pass
    try:
        post_data['post_bbcode_url'] = post.xpath('div/a[@class="thickbox"]')[0].get('href').split('?')[0]
    except:
        pass
    return post_data


def main(input_fname):
    html = lxml.html.parse(input_fname)
    data = {
        'thread_id': get_thread_id(html),
        'posts': map(process_post, post_selector(html))
    }
    print json.dumps(data)

if __name__ == '__main__':
    plac.call(main)
