

import json
import twitter
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


BOT_ID = 67346249
FIRST = 29486484025249792

creds = api.VerifyCredentials()
statuses_count = creds.statuses_count
logging.info('Status count={0}'.format(statuses_count))

while True:
    for t in api.GetUserTimeline(BOT_ID, count=2000):
        if t.id == FIRST:
            break

        try:
            api.DestroyStatus(t.id)
            logging.info((t.created_at, t.id, t.in_reply_to_screen_name, t.text,))
            statuses_count -= 1
        except Exception:
            pass

    if statuses_count % 1000 == 0:
        logging.info('Status count={0}'.format(statuses_count))

    if statuses_count <= 0:
        break
