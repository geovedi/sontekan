import twitter
import time
import json
import requests
import regex as re
from joblib import Parallel, delayed
import logging

logging.basicConfig(
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)

config = json.load(open('auth.begobet.json'))

api = twitter.Api(
    consumer_key=config['CONSUMER_KEY'],
    consumer_secret=config['CONSUMER_SECRET'],
    access_token_key=config['ACCESS_TOKEN_KEY'],
    access_token_secret=config['ACCESS_TOKEN_SECRET'],
    sleep_on_rate_limit=True
)


base_url = ('https://twitter.com/i/profiles/show/begobet/timeline/'
            'tweets?include_available_features=1&include_entities=1'
            '&max_position={0}&reset_error_state=false')

MAX_ID = 62239949000409088
RETRY = 0
FIRST = 29486484025249792
pat = re.compile(r'data-item-id="(\d+)"')

def destroy(tid):
    try:
        t = api.DestroyStatus(tid, trim_user=True)
        logging.info((t.created_at, t.id, t.in_reply_to_screen_name,
            t.text,))
    except twitter.TwitterError:
        pass

while True:
    if RETRY >= 10:
        break

    try:
        resp = requests.get(base_url.format(MAX_ID))
        statuses = pat.findall(resp.json()['items_html'])
        statuses = set(map(int, statuses))
        if FIRST in statuses:
            statuses.remove(FIRST)
        if not statuses:
            raise Exception('Empty statuses')
        RETRY = 0
    except Exception as e:
        logging.error(e)
        RETRY += 1
        time.sleep(10)
        continue

    Parallel(n_jobs=2)(delayed(destroy)(i) for i in statuses)
    MAX_ID = min(statuses)
    statuses = set()

