import json
import csv
import twitter
import logging
from joblib import Parallel, delayed

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

logging.info(api.VerifyCredentials())

FIRST = 29486484025249792

statuses = [int(t['tweet_id']) for t in csv.DictReader(open('tweets.csv'))]

def destroy(tid):
    if tid == FIRST:
        return
    try:
        t = api.DestroyStatus(tid, trim_user=True)
        logging.info((t.created_at, t.id, t.in_reply_to_screen_name,
            t.text,))
    except twitter.TwitterError:
        pass

Parallel(n_jobs=4)(delayed(destroy)(i) for i in statuses)

