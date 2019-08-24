import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

import copy
import threading
import time
import random
import shelve
import string

import feed

from flask import abort, Flask, request
from flask_cors import CORS

CACHE_LENGTH = 300
DATA_FILE = 'data/data'

news_index = 0

with shelve.open(DATA_FILE) as db:
    logging.info('Reading caches from disk...')
    news_list = db.get('news_list', [])
    news_ref_to_id = db.get('news_ref_to_id', {})
    news_cache = db.get('news_cache', {})

flask_app = Flask(__name__)
cors = CORS(flask_app)

@flask_app.route('/')
def index():
    front_page = [news_cache[news_ref_to_id[ref]] for ref in news_list]
    front_page = [copy.deepcopy(x) for x in front_page if 'title' in x]
    for story in front_page:
        if 'comments' in story: story.pop('comments')
        if 'text' in story: story.pop('text')
    return {'stories': front_page}

@flask_app.route('/<id>')
def comments(id):
    if id in news_cache:
        return {'story': news_cache[id]}

    with shelve.open(DATA_FILE) as db:
        if id in db:
            return {'story': db[id]}

    abort(404)

print('Starting Flask...')
web_thread = threading.Thread(target=flask_app.run, kwargs={'port': 33842})
web_thread.setDaemon(True)
web_thread.start()

def gen_rand_id():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(4))

def new_id():
    nid = gen_rand_id()
    with shelve.open(DATA_FILE) as db:
        while nid in news_cache or nid in db:
            nid = gen_rand_id()
    return nid

try:
    while True:
        if news_index == 0:
            feed_list = feed.list()
            new_items = [(ref, source) for ref, source in feed_list if ref not in news_list]
            for ref, source in new_items:
                news_list.insert(0, ref)
                nid = new_id()
                news_ref_to_id[ref] = nid
                news_cache[nid] = dict(id=nid, ref=ref, source=source)

            if len(new_items):
                logging.info('Added {} new refs.'.format(len(new_items)))

            while len(news_list) > CACHE_LENGTH:
                old_ref = news_list.pop()
                old_story = news_cache.pop(news_ref_to_id[old_ref])
                old_id = news_ref_to_id.pop(old_ref)
                logging.info('Removed ref {} id {}.'.format(old_ref, old_id))
                with shelve.open(DATA_FILE) as db:
                    db[old_id] = old_story

        if news_index < len(news_list):
            update_ref = news_list[news_index]
            update_id = news_ref_to_id[update_ref]
            news_story = news_cache[update_id]
            feed.update_story(news_story)

        time.sleep(1)

        news_index += 1
        if news_index == CACHE_LENGTH: news_index = 0

finally:
    with shelve.open(DATA_FILE) as db:
        logging.info('Writing caches to disk...')
        db['news_list'] = news_list
        db['news_ref_to_id'] = news_ref_to_id
        db['news_cache'] = news_cache
