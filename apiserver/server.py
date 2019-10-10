import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

import copy
import threading
import time
import shelve
from urllib.parse import urlparse

import feed
from utils import gen_rand_id

from flask import abort, Flask, request, render_template
from werkzeug.exceptions import NotFound
from flask_cors import CORS

CACHE_LENGTH = 300
DATA_FILE = 'data/data'

news_index = 0

with shelve.open(DATA_FILE) as db:
    logging.info('Reading caches from disk...')
    news_list = db.get('news_list', [])
    news_ref_to_id = db.get('news_ref_to_id', {})
    news_cache = db.get('news_cache', {})

def get_story(id):
    if id in news_cache:
        return {'story': news_cache[id]}
    with shelve.open(DATA_FILE) as db:
        if id in db:
            return {'story': db[id]}
    return None

build_folder = '../webclient/build'
flask_app = Flask(__name__, template_folder=build_folder, static_folder=build_folder, static_url_path='')
cors = CORS(flask_app)

@flask_app.route('/api')
def api():
    front_page = [news_cache[news_ref_to_id[ref]] for ref in news_list]
    front_page = [copy.copy(x) for x in front_page if 'text' in x and x['text']][:100]
    for story in front_page:
        if 'comments' in story: story.pop('comments')
        if 'text' in story: story.pop('text')
    return {'stories': front_page}

@flask_app.route('/api/<id>')
def story(id):
    return get_story(id) or abort(404)

@flask_app.route('/')
def index():
    return render_template('index.html',
            title='Feed',
            url='news.t0.vc',
            description='Reddit, Hacker News, and Tildes combined, then pre-rendered in reader mode')

@flask_app.route('/<id>', strict_slashes=False)
@flask_app.route('/<id>/c', strict_slashes=False)
def static_story(id):
    try:
        return flask_app.send_static_file(id)
    except NotFound:
        pass

    story = get_story(id)
    if story:
        story = story['story']
    else:
        return abort(404)

    score = story['score']
    num_comments = story['num_comments']
    source = story['source']
    description = '{} point{}, {} comment{} on {}'.format(
            score, 's' if score != 1 else '',
            num_comments, 's' if num_comments != 1 else '',
            source)
    url = urlparse(story['url']).hostname.replace('www.', '')

    return render_template('index.html',
            title=story['title'],
            url=url,
            description=description)

print('Starting Flask...')
web_thread = threading.Thread(target=flask_app.run, kwargs={'port': 33842})
web_thread.setDaemon(True)
web_thread.start()

def new_id():
    nid = gen_rand_id()
    with shelve.open(DATA_FILE) as db:
        while nid in news_cache or nid in db:
            nid = gen_rand_id()
    return nid

def remove_ref(old_ref, archive=False):
    while old_ref in news_list:
        news_list.remove(old_ref)
    old_story = news_cache.pop(news_ref_to_id[old_ref])
    old_id = news_ref_to_id.pop(old_ref)
    logging.info('Removed ref {} id {}.'.format(old_ref, old_id))
    if archive:
        with shelve.open(DATA_FILE) as db:
            db[old_id] = old_story

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
                old_ref = news_list[-1]
                remove_ref(old_ref, archive=True)

        if news_index < len(news_list):
            update_ref = news_list[news_index]
            update_id = news_ref_to_id[update_ref]
            news_story = news_cache[update_id]
            valid = feed.update_story(news_story)
            if not valid:
                remove_ref(update_ref)

        time.sleep(3)

        news_index += 1
        if news_index == CACHE_LENGTH: news_index = 0

finally:
    with shelve.open(DATA_FILE) as db:
        logging.info('Writing caches to disk...')
        db['news_list'] = news_list
        db['news_ref_to_id'] = news_ref_to_id
        db['news_cache'] = news_cache
