import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

import copy
import threading
import time
import random
import requests
import string

from feeds import hackernews
from flask import abort, Flask, request
from flask_cors import CORS

CACHE_LENGTH = 300
READ_API = 'http://127.0.0.1:33843'

news_index = 0
news_list = []
news_ref_to_id = {}
news_cache = {}

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
    else:
        abort(404)

print('Starting Flask...')
web_thread = threading.Thread(target=flask_app.run, kwargs={'port': 33842})
web_thread.setDaemon(True)
web_thread.start()

def new_id():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(4))

def get_article(url):
    try:
        r = requests.post(READ_API, data=dict(url=url), timeout=10)

        if r.status_code != 200:
            raise

        return r.text
    except:
        return '<p>Problem parsing article :(</p>'

while True:
    if news_index == 0:
        feed = hackernews.feed()
        new_refs = [ref for ref in feed if ref not in news_list]
        for ref in new_refs:
            news_list.insert(0, ref)
            nid = new_id()
            news_ref_to_id[ref] = nid
            news_cache[nid] = dict(id=nid, ref=ref)

        if len(new_refs):
            logging.info('Added {} new refs.'.format(len(new_refs)))

        while len(news_list) > CACHE_LENGTH:
            old_ref = news_list.pop()
            del news_cache[news_ref_to_id[old_ref]]
            del news_ref_to_id[old_ref]
            logging.info('Removed ref {}.'.format(old_ref))

    if news_index < len(news_list):
        update_ref = news_list[news_index]
        update_id = news_ref_to_id[update_ref]
        news_story = news_cache[update_id]
        story = hackernews.story(update_ref)
        if story:
            news_story.update(story)
        if news_story.get('url', '') and not news_story.get('text', ''):
            news_story['text'] = get_article(news_story['url'])

    time.sleep(1)

    news_index += 1
    if news_index == CACHE_LENGTH: news_index = 0
