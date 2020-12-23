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

def source_to_story(source, with_text=False):
    story = {}
    story.update(source.data)
    story['source'] = source.source
    story['id'] = source.sid
    story['ref'] = source.ref
    story['excerpt'] = source.content.details.get('excerpt', '')
    if with_text:
        story['text'] = source.content.details.get('content', '')
        story['meta_links'] = source.content.details.get('meta', {}).get('links', [])
        story['scraper'] = source.content.details.get('scraper', '')
        story['scraper_link'] = source.content.details.get('scraper_link', '')
    else:
        story['comments'] = []
    return story

def content_to_story(content, with_text=True):
    related = []
    story = {
        'source': 'manual',
        'title': content.details.get('title', ''),
        'author': content.details.get('author', ''),
        'url': content.url,
        'excerpt': content.details.get('excerpt', ''),
    }
    if with_text:
        story['text'] = content.details.get('content', '')
        story['meta_links'] =content.details.get('meta', {}).get('links', [])
        story['scraper'] = content.details.get('scraper', '')
        story['scraper_link'] =content.details.get('scraper_link', '')
    if content.sources:
        for source in content.sources:
            source.content = content
        related = [source_to_story(source) for source in content.sources]
        story.update(source_to_story(content.sources[0], with_text=True))
    return story, related

@flask_app.route('/api')
@flask_app.route('/api/feed')
def api_feed():
    skip = request.args.get('skip', 0)
    limit = request.args.get('limit', 20)
    sources = database.get_feed(skip=skip, limit=limit)
    stories = [source_to_story(source) for source in sources]
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

@flask_app.route('/api/submit', methods=['POST'], strict_slashes=False)
def submit():
    try:
        url = request.form['url']
        ref, source = feed.get_ref_from_url(url)
        
        existing = database.get_source_by_ref(ref, source)
        if existing:
            return {'nid': existing.sid}
        existing = database.get_content_by_url(url)
        if existing:
            return {'nid': existing.sources[0].sid}
        else:
            item = database.Queue(ref=ref, source=source)
            data = feed.update_source(item, is_manual=True)
            if not data:
                raise Exception('Invalid article')

            details, scraper = feed.scrape_url(url)
            if not details:
                raise Exception('Invalid article')

            database.put_content(dict(details=details, scraper=scraper, url=data.get('url')))
            database.put_source(dict(data=data, source=source, ref=ref, url=data.get('url')))
            output = database.get_source_by_ref(ref, source)
            if output:
                search.put_story(source_to_story(output))
                return {'nid': output.sid}

    except BaseException as e:
        logging.error('Problem with article submission: {} - {}'.format(e.__class__.__name__, str(e)))
        print(traceback.format_exc())
        abort(400)


@flask_app.route('/api/<sid>')
def story(sid):
    skip = request.args.get('skip', 0)
    limit = request.args.get('limit', 20)
    source = database.get_source(sid)
    story = source_to_story(source, with_text=True)
    related = []
    if source.content:
        content = database.get_content(source.content.cid)
        _, related = content_to_story(content)

    links = []
    for url in story.get('meta_links', []):
        content = database.get_content_by_url(url)
        if content:
            s, r = content_to_story(content, with_text=False)
            links += [s]
    res = Response(json.dumps({"story": story, "related": related, "links": links }))
    res.headers['content-type'] = 'application/json'
    return res

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
            gevent.sleep(1)
            added.append((ref, source))
        except KeyboardInterrupt:
            raise
        except database.IntegrityError:
            # logging.info('Unable to add ref ' + ref)
            continue
    return added

def _add_current_story(item):
    source = feed.update_source(item)
    if source:
        content = source.pop('content', None)
        try:
            database.put_source(dict(data=source, source=item.source, ref=item.ref, url=source.get('url')))
        except KeyboardInterrupt:
            raise
        except database.IntegrityError:
            logging.info(f'Unable to add story with ref {item.ref}')

        if content:
            try:
                database.put_content(content)
            except KeyboardInterrupt:
                raise
            except database.IntegrityError:
                logging.info(f'Added content for ref {item.ref}')

        s = database.get_source_by_ref(item.ref, item.source)
        content = s.content
        search.put_story(source_to_story(s))
        if content:
            c = database.get_content(content.cid)
            _, related = content_to_story(c, with_text=True)
            for story in related:
                search.put_story(story)
        if s:
            database.del_queue(item.ref, item.source)

    else:
        logging.info(f'ref {item.ref} not processed')

def queue_thread():
    logging.info('Starting Queue thread...')
    try:
        while True:
            added = _add_stories()
            logging.info('Added {} new refs'.format(len(added)))
            gevent.sleep(600)
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
                _add_current_story(item)
                gevent.sleep(1)

            gevent.sleep(20)

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
            sources = database.get_source_for_scraping()
            contents = database.get_content_for_scraping()
            urls = [source.url for source in sources]
            urls += [content.url for content in contents]
            for url in urls:
                logging.info(f'Scraping {url}')
                details, scraper = feed.scrape_url(url)
                if not details:
                    logging.info(f'No details to scrape, skipping {url}...')
                    continue
                database.put_content(dict(details=details, scraper=scraper, url=url))
                content = database.get_content_by_url(url)
                _, related = content_to_story(content, with_text=True)
                for story in related:
                    search.put_story(story)
                gevent.sleep(1)
                # links = details.get('meta', {}).get('links', [])
                # for link in links:
                #     database.put_content(dict(url=link))
            gevent.sleep(20)

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
