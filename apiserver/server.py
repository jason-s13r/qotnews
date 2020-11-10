import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

import gevent
from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer

import copy
import json
import threading
import traceback
import time
from urllib.parse import urlparse, parse_qs

import settings
import database
import search
import feed
from utils import gen_rand_id

from flask import abort, Flask, request, render_template, stream_with_context, Response
from werkzeug.exceptions import NotFound
from flask_cors import CORS

database.init()
search.init()

def new_id():
    nid = gen_rand_id()
    while database.get_story(nid):
        nid = gen_rand_id()
    return nid

build_folder = '../webclient/build'
flask_app = Flask(__name__, template_folder=build_folder, static_folder=build_folder, static_url_path='')
cors = CORS(flask_app)

@flask_app.route('/api')
def api():
    stories = database.get_stories(settings.MAX_STORY_AGE)
    res = Response(json.dumps({"stories": stories}))
    res.headers['content-type'] = 'application/json'
    return res

@flask_app.route('/api/search', strict_slashes=False)
def apisearch():
    q = request.args.get('q', '')
    if len(q) >= 3:
        results = search.search(q)
    else:
        results = []
    return dict(results=results)

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
        elif 'news.t0.vc' in parse.hostname:
            raise Exception('Invalid article')
        else:
            source = 'manual'
            ref = url

        existing = database.get_story_by_ref(ref)
        if existing:
            return {'nid': existing.sid}
        else:
            story = dict(id=nid, ref=ref, source=source)
            valid = feed.update_story(story, is_manual=True)
            if valid:
                database.put_story(story)
                search.put_story(story)
                return {'nid': nid}
            else:
                raise Exception('Invalid article')

    except BaseException as e:
        logging.error('Problem with article submission: {} - {}'.format(e.__class__.__name__, str(e)))
        print(traceback.format_exc())
        abort(400)


@flask_app.route('/api/<sid>')
def story(sid):
    story = database.get_story(sid)
    if story:
        related = database.get_stories_by_url(story.meta['url'])
        related = [r.meta for r in related]
        res = Response(json.dumps({"story": story.data, "related": related}))
        res.headers['content-type'] = 'application/json'
        return res
    else:
        return abort(404)

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

    story = database.get_story(sid)
    if not story: return abort(404)
    story = story.data

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

def _add_new_refs():
    for ref, source in feed.get_list():
        if database.get_story_by_ref(ref):
            continue
        try:
            nid = new_id()
            database.put_ref(ref, nid, source)
            logging.info('Added ref ' + ref)
        except database.IntegrityError:
            continue

def _update_current_story(item):
    try:
        story = database.get_story(item['sid']).data
    except AttributeError:
        story = dict(id=item['sid'], ref=item['ref'], source=item['source'])

    logging.info('Updating story: {}'.format(str(story['ref'])))

    valid = feed.update_story(story)
    if valid:
        database.put_story(story)
        search.put_story(story)
    else:
        database.del_ref(item['ref'])
        logging.info('Removed ref {}'.format(item['ref']))

def feed_thread():
    ref_list = []
    try:
        while True:
            # onboard new stories
            if not len(ref_list):
                _add_new_refs()
                ref_list = database.get_reflist()

            # update current stories
            if len(ref_list):
                item = ref_list.pop(0)
                _update_current_story(item)

            gevent.sleep(6)

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
