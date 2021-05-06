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
from datetime import datetime, timedelta
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
    skip = request.args.get('skip', 0)
    limit = request.args.get('limit', 20)
    stories = database.get_stories(skip=skip, limit=limit)
    res = Response(json.dumps({"stories": stories}))
    res.headers['content-type'] = 'application/json'
    return res

@flask_app.route('/api/search', strict_slashes=False)
def apisearch():
    q = request.args.get('q', '')
    skip = request.args.get('skip', 0)
    limit = request.args.get('limit', 20)
    if len(q) >= 3:
        results = search.search(q, skip=skip, limit=limit)
    else:
        results = []
    return dict(results=results)

@flask_app.route('/api/submit', methods=['POST'], strict_slashes=False)
def submit():
    try:
        url = request.form['url']
        nid = new_id()
        parse = urlparse(url)

        if settings.HOSTNAME in parse.hostname:
            raise Exception('Invalid URL')

        source, ref, urlref = feed.get_source_ref(url, parse)

        if not source or not ref:
            source = 'manual'
            ref = url
            urlref = url

        existing = database.get_story_by_ref(ref)
        if existing:
            return {'nid': existing.sid}
        
        existing = database.get_story_by_url(url)
        if existing:
            return {'nid': existing.sid}
        else:
            story = dict(id=nid, ref=ref, source=source)
            valid = feed.update_story(story, is_manual=True, urlref=urlref)
            if valid:
                if source is not "manual":
                    database.put_ref(ref, nid, source, urlref)
                database.put_story(story)
                search.put_story(story)
                return {'nid': nid}
            else:
                logging.info(str(story))
                raise Exception('Invalid article')

    except BaseException as e:
        logging.error('Problem with article submission: {} - {}'.format(e.__class__.__name__, str(e)))
        print(traceback.format_exc())
        abort(400)


@flask_app.route('/api/<sid>')
def story(sid):
    story = database.get_story(sid)
    if story:
        related = []
        if story.meta['url']:
            related = database.get_stories_by_url(story.meta['url'])
            related = [r.meta for r in related]
        links = story.meta.get('meta_links', [])
        if links:
            links = [database.get_story_by_url(link) for link in links]
            links = list(filter(None,  [l.meta if l else None for l in links]))
        res = Response(json.dumps({"story": story.data, "related": related, "links": links}))
        res.headers['content-type'] = 'application/json'
        return res
    else:
        return abort(404)

@flask_app.route('/')
@flask_app.route('/search')
def index():
    return render_template('index.html',
            title='Feed',
            url=settings.HOSTNAME,
            description='Hacker News, Reddit, Lobsters, and Tildes articles rendered in reader mode')

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

http_server = WSGIServer(('', settings.API_PORT or 33842), flask_app)

def _add_new_refs():
    added = []
    for ref, source, urlref in feed.get_list():
        if database.get_story_by_ref(ref):
            continue
        try:
            nid = new_id()
            database.put_ref(ref, nid, source, urlref)
            logging.info('Added ref ' + ref)
            added.append(ref)
            gevent.sleep(1)
        except database.IntegrityError:
            #logging.info('Unable to add ref ' + ref)
            continue
    return added

def _update_current_story(item):
    try:
        story = database.get_story(item['sid']).data
    except AttributeError:
        story = dict(id=item['sid'], ref=item['ref'], source=item['source'])

    logging.info('Updating story: {}'.format(str(story['ref'])))

    valid = feed.update_story(story, urlref=item['urlref'])
    if valid:
        try:
            database.put_story(story)
            search.put_story(story)
            if story['source'] == 'manual':
                database.del_ref(item['ref'])
                logging.info('Removed manual ref {}'.format(item['ref']))
        except database.IntegrityError:
            logging.info('Unable to add story with ref ' + item['ref'])
    else:
        database.del_ref(item['ref'])
        logging.info('Removed ref {}'.format(item['ref']))


def feed_thread():
    new_refs = []
    update_refs = []
    last_check = datetime.now() - timedelta(minutes=20)
    try:
        while True:
            # onboard new stories
            time_since_check = datetime.now() - last_check
            if not len(new_refs) and time_since_check > timedelta(minutes=15):
                added = _add_new_refs()
                ref_list = database.get_reflist()
                new_refs = list(filter(None, [i if i['ref'] in added else None for i in ref_list]))
                update_queue = list(filter(None, [i if i['ref'] not in added else None for i in ref_list]))
                current_queue_refs = [i['ref'] for i in update_refs]
                update_queue = list(filter(None, [i if i['ref'] not in current_queue_refs else None for i in update_queue]))
                update_refs += update_queue
                logging.info('Added {} new refs'.format(len(added)))
                logging.info('Have {} refs in update queue'.format(len(current_queue_refs)))
                logging.info('Fetched {} refs for update queue'.format(len(update_queue)))
                last_check = datetime.now()
                gevent.sleep(5)

            # update new stories
            if len(new_refs):
                item = new_refs.pop(0)
                logging.info('Processing new story ref {}'.format(item['ref']))
                _update_current_story(item)
                gevent.sleep(5)

            # update current stories
            if len(update_refs):
                item = update_refs.pop(0)
                logging.info('Processing existing story ref {}'.format(item['ref']))
                _update_current_story(item)
                gevent.sleep(5)

            gevent.sleep(10)

    except KeyboardInterrupt:
        logging.info('Ending feed thread...')
    except ValueError as e:
        logging.error('feed_thread error: {} {}'.format(e.__class__.__name__, e))

    http_server.stop()
    gevent.kill(feed_thread_ref)


print('Starting Feed thread...')
feed_thread_ref = gevent.spawn(feed_thread)

print('Starting HTTP thread...')
try:
    http_server.serve_forever()
except KeyboardInterrupt:
    gevent.kill(feed_thread_ref)
    logging.info('Exiting...')
