import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

import copy
import threading
import traceback
import time
import shelve
from urllib.parse import urlparse, parse_qs

import archive
import feed
from utils import gen_rand_id

from flask import abort, Flask, request, render_template, stream_with_context, Response
from werkzeug.exceptions import NotFound
from flask_cors import CORS

import gevent
from gevent import monkey
from gevent.pywsgi import WSGIServer

monkey.patch_all()

archive.init()

CACHE_LENGTH = 150
DATA_FILE = 'data/data'

news_index = 0

with shelve.open(DATA_FILE) as db:
    logging.info('Reading caches from disk...')
    news_list = db.get('news_list', [])
    news_ref_to_id = db.get('news_ref_to_id', {})
    news_cache = db.get('news_cache', {})

    # clean cache if broken
    try:
        for ref in news_list:
            nid = news_ref_to_id[ref]
            _ = news_cache[nid]
    except KeyError as e:
        ekey = str(e)
        logging.error('Unable to find key {}. Trying to remove...'.format(ekey))
        if ekey in news_cache:
            news_cache.remove(ekey)
        if ekey in news_list:
            news_list.remove(ekey)
        if ekey in news_ref_to_id:
            news_ref_to_id.remove(ekey)

def get_story(sid):
    if sid in news_cache:
        return news_cache[sid]
    else:
        return archive.get_story(sid)

def new_id():
    nid = gen_rand_id()
    while nid in news_cache or archive.get_story(nid):
        nid = gen_rand_id()
    return nid

def remove_ref(old_ref):
    while old_ref in news_list:
        news_list.remove(old_ref)
    old_story = news_cache.pop(news_ref_to_id[old_ref])
    old_id = news_ref_to_id.pop(old_ref)
    logging.info('Removed ref {} id {}.'.format(old_ref, old_id))

build_folder = '../webclient/build'
flask_app = Flask(__name__, template_folder=build_folder, static_folder=build_folder, static_url_path='')
cors = CORS(flask_app)

@flask_app.route('/api')
def api():
    try:
        front_page = [news_cache[news_ref_to_id[ref]] for ref in news_list]
    except KeyError as e:
        ekey = str(e)
        logging.error('Unable to find key {}. Trying to remove...'.format(ekey))
        if ekey in news_cache:
            news_cache.remove(ekey)
        if ekey in news_list:
            news_list.remove(ekey)

    front_page = [copy.copy(x) for x in front_page if 'title' in x and x['title']]
    front_page = front_page[:60]
    for story in front_page:
        story.pop('text', None)
        story.pop('comments', None)

    return {'stories': front_page}

@flask_app.route('/api/search', strict_slashes=False)
def search():
    search = request.args.get('q', '')
    if len(search) >= 3:
        res = archive.search(search)
    else:
        res = []
    return {'results': res}

@flask_app.route('/api/submit', methods=['POST'], strict_slashes=False)
def submit():
    try:
        url = request.form['url']
        nid = new_id()

        parse = urlparse(url)
        if 'news.ycombinator.com' in parse.hostname:
            source = 'hackernews'
            ref = parse_qs(parse.query)['id'][0]
        elif 'tildes.net' in parse.hostname and '~' in url:
            source = 'tildes'
            ref = parse.path.split('/')[2]
        elif 'reddit.com' in parse.hostname and 'comments' in url:
            source = 'reddit'
            ref = parse.path.split('/')[4]
        else:
            source = 'manual'
            ref = url

        news_story = dict(id=nid, ref=ref, source=source)
        news_cache[nid] = news_story
        valid = feed.update_story(news_story, is_manual=True)
        if valid:
            archive.update(news_story)
            return {'nid': nid}
        else:
            news_cache.pop(nid, '')
            raise Exception('Invalid article')

    except BaseException as e:
        logging.error('Problem with article submission: {} - {}'.format(e.__class__.__name__, str(e)))
        print(traceback.format_exc())
        abort(400)


@flask_app.route('/api/<sid>')
def story(sid):
    story = get_story(sid)
    return dict(story=story) if story else abort(404)

@flask_app.route('/')
@flask_app.route('/search')
def index():
    return render_template('index.html',
            title='Feed',
            url='news.t0.vc',
            description='Reddit, Hacker News, and Tildes combined, then pre-rendered in reader mode')

@flask_app.route('/<sid>', strict_slashes=False)
@flask_app.route('/<sid>/c', strict_slashes=False)
def static_story(sid):
    try:
        return flask_app.send_static_file(sid)
    except NotFound:
        pass

    story = get_story(sid)
    if not story: return abort(404)

    score = story['score']
    num_comments = story['num_comments']
    source = story['source']
    description = '{} point{}, {} comment{} on {}'.format(
            score, 's' if score != 1 else '',
            num_comments, 's' if num_comments != 1 else '',
            source)
    url = urlparse(story['url']).hostname or urlparse(story['link']).hostname or ''
    url = url.replace('www.', '')

    return render_template('index.html',
            title=story['title'],
            url=url,
            description=description)

http_server = WSGIServer(('', 33842), flask_app)

def feed_thread():
    global news_index

    try:
        while True:
            # onboard new stories
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

                # drop old ones
                while len(news_list) > CACHE_LENGTH:
                    old_ref = news_list[-1]
                    remove_ref(old_ref)

            # update current stories
            if news_index < len(news_list):
                try:
                    update_ref = news_list[news_index]
                    update_id = news_ref_to_id[update_ref]
                    news_story = news_cache[update_id]
                except KeyError as e:
                    ekey = str(e)
                    logging.error('Unable to find key {}. Trying to remove...'.format(ekey))
                    if ekey in news_cache:
                        news_cache.remove(ekey)
                    if ekey in news_list:
                        news_list.remove(ekey)
                    if ekey in news_ref_to_id:
                        news_ref_to_id.remove(ekey)
                valid = feed.update_story(news_story)
                if valid:
                    archive.update(news_story)
                else:
                    remove_ref(update_ref)
            else:
                logging.info('Skipping update - no story #' + str(news_index+1))

            gevent.sleep(6)

            news_index += 1
            if news_index == CACHE_LENGTH: news_index = 0

    except KeyboardInterrupt:
        logging.info('Ending feed thread...')
    except ValueError as e:
        logging.error('feed_thread error: {} {}'.format(e.__class__.__name__, e))
        http_server.stop()

print('Starting Feed thread...')
gevent.spawn(feed_thread)

print('Starting HTTP thread...')
try:
    http_server.serve_forever()
except KeyboardInterrupt:
    logging.info('Exiting...')
finally:
    with shelve.open(DATA_FILE) as db:
        logging.info('Writing caches to disk...')
        db['news_list'] = news_list
        db['news_ref_to_id'] = news_ref_to_id
        db['news_cache'] = news_cache
