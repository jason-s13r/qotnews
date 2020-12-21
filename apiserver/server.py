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

@flask_app.route('/api/source')
@flask_app.route('/api/source/<sid>')
def api_source(sid=None):
    sources = database.get_source(sid)
    text = json.dumps(sources, cls=database.new_alchemy_encoder(), check_circular=False)
    res = Response(text)
    res.headers['content-type'] = 'application/json'
    return res

@flask_app.route('/api/content')
@flask_app.route('/api/content/<cid>')
def api_contents(cid=None):
    contents = database.get_content(cid)
    text = json.dumps(contents, cls=database.new_alchemy_encoder(), check_circular=False)
    res = Response(text)
    res.headers['content-type'] = 'application/json'
    return res

@flask_app.route('/api/queued')
def api_queued():
    queue = database.get_queue()
    text = json.dumps(queue, cls=database.new_alchemy_encoder(), check_circular=False)
    res = Response(text)
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

# @flask_app.route('/api/submit', methods=['POST'], strict_slashes=False)
# def submit():
#     try:
#         url = request.form['url']
#         nid = new_id()

#         parse = urlparse(url)
#         if 'news.ycombinator.com' in parse.hostname:
#             source = 'hackernews'
#             ref = parse_qs(parse.query)['id'][0]
#         elif 'tildes.net' in parse.hostname and '~' in url:
#             source = 'tildes'
#             ref = parse.path.split('/')[2]
#         elif 'lobste.rs' in parse.hostname and '/s/' in url:
#             source = 'lobsters'
#             ref = parse.path.split('/')[2]
#         elif 'reddit.com' in parse.hostname and 'comments' in url:
#             source = 'reddit'
#             ref = parse.path.split('/')[4]
#         elif settings.HOSTNAME in parse.hostname:
#             raise Exception('Invalid URL')
#         else:
#             source = 'manual'
#             ref = url

#         existing = database.get_story_by_ref(ref)
#         if existing:
#             return {'nid': existing.sid}
        
#         existing = database.get_story_by_url(url)
#         if existing:
#             return {'nid': existing.sid}
#         else:
#             story = dict(id=nid, ref=ref, source=source)
#             valid = feed.update_story(story, is_manual=True)
#             if valid:
#                 database.put_story(story)
#                 database.put_source(story)
#                 search.put_story(story)
#                 return {'nid': nid}
#             else:
#                 logging.info(str(story))
#                 raise Exception('Invalid article')

#     except BaseException as e:
#         logging.error('Problem with article submission: {} - {}'.format(e.__class__.__name__, str(e)))
#         print(traceback.format_exc())
#         abort(400)


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

def _add_stories():
    added = []
    for ref, source, url in feed.get_list():
        queued = database.get_queue(ref, source)
        if queued:
            continue
        try:
            database.put_queue(ref, source, url)
            logging.info('Queued ref ' + ref)
            added.append((ref, source))
        except KeyboardInterrupt:
            raise
        except database.IntegrityError:
            # logging.info('Unable to add ref ' + ref)
            continue
    return added

def _update_current_story(item):
    source = feed.update_source(item)
    if source:
        content = source.pop('content', None)
        try:
            database.put_source(dict(data=source, source=item.source, url=source.get('url')))
            database.del_queue(item.ref, item.source)
        except KeyboardInterrupt:
            raise
        except database.IntegrityError:
            logging.info(f'Unable to add story with ref {item.ref}')

        if not content:
            content = dict(url=source.get('url'))
            
        try:
            database.put_content(content)
        except KeyboardInterrupt:
            raise
        except database.IntegrityError:
            logging.info(f'Added content for ref {item.ref}')
    else:
        logging.info(f'ref {item.ref} not processed')

def queue_thread():
    logging.info('Starting Queue thread...')
    try:
        while True:
            added = _add_stories()
            logging.info('Added {} new refs'.format(len(added)))
            gevent.sleep(60*10)
    except KeyboardInterrupt:
        logging.info('Ending _queue_new_refs...')
    except ValueError as e:
        logging.error('feed_thread error: {} {}'.format(e.__class__.__name__, e))

    http_server.stop()
    gevent.kill(feed_thread_ref)
    gevent.kill(queue_thread_ref)
    gevent.kill(scrape_thread_ref)

def feed_thread():
    logging.info('Starting Feed thread...')
    try:
        while True:
            queue = database.get_queue()
            for item in queue:
                logging.info(f'Processing story ref {item.ref}')
                _update_current_story(item)
                gevent.sleep(1)

            gevent.sleep(10)

    except KeyboardInterrupt:
        logging.info('Ending feed thread...')
    except ValueError as e:
        logging.error('feed_thread error: {} {}'.format(e.__class__.__name__, e))
        feed_thread()

    http_server.stop()
    gevent.kill(feed_thread_ref)
    gevent.kill(queue_thread_ref)
    gevent.kill(scrape_thread_ref)

def scrape_thread():
    logging.info('Starting Scrape thread...')
    try:
        while True:
            contents = database.get_content_for_scraping()
            for content in contents:
                logging.info(f'Scraping {content.url}')
                details, scraper = feed.scrape_url(content.url)
                if details:
                    content.details = details
                content.scraper= scraper
                database.put_content(database.as_dict(content))
                gevent.sleep(1)
            gevent.sleep(10)

    except KeyboardInterrupt:
        logging.info('Ending Scrape thread...')
    except ValueError as e:
        logging.error('scrape_thread error: {} {}'.format(e.__class__.__name__, e))
        scrape_thread()

    http_server.stop()
    gevent.kill(feed_thread_ref)
    gevent.kill(queue_thread_ref)
    gevent.kill(scrape_thread_ref)

queue_thread_ref = gevent.spawn(queue_thread)
feed_thread_ref = gevent.spawn(feed_thread)
scrape_thread_ref = gevent.spawn(scrape_thread)

print('Starting HTTP thread...')
try:
    http_server.serve_forever()
except KeyboardInterrupt:
    gevent.kill(feed_thread_ref)
    gevent.kill(queue_thread_ref)
    gevent.kill(scrape_thread_ref)
    logging.info('Exiting...')
