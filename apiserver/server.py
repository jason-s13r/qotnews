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

import database
import search
import feed
from utils import gen_rand_id

from flask import abort, Flask, request, render_template, stream_with_context, Response
from werkzeug.exceptions import NotFound
from flask_cors import CORS

database.init()
search.init()

FEED_LENGTH = 75
news_index = 0

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
    stories = database.get_stories(FEED_LENGTH)
    # hacky nested json
    res = Response('{"stories":[' + ','.join(stories) + ']}')
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
        # hacky nested json
        res = Response('{"story":' + story.full_json + '}')
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
    story = json.loads(story.full_json)

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
                for ref, source in feed.list():
                    if database.get_story_by_ref(ref):
                        continue
                    try:
                        nid = new_id()
                        database.put_ref(ref, nid, source)
                        logging.info('Added ref ' + ref)
                    except database.IntegrityError:
                        continue

            ref_list = database.get_reflist(FEED_LENGTH)

            # update current stories
            if news_index < len(ref_list):
                item = ref_list[news_index]

                try:
                    story_json = database.get_story(item['sid']).full_json
                    story = json.loads(story_json)
                except AttributeError:
                    story = dict(id=item['sid'], ref=item['ref'], source=item['source'])

                logging.info('Updating story: ' + str(story['ref']) + ', index: ' + str(news_index))

                valid = feed.update_story(story)
                if valid:
                    database.put_story(story)
                    search.put_story(story)
                else:
                    database.del_ref(item['ref'])
                    logging.info('Removed ref {}'.format(item['ref']))
            else:
                logging.info('Skipping index: ' + str(news_index))

            gevent.sleep(6)

            news_index += 1
            if news_index == FEED_LENGTH: news_index = 0

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
