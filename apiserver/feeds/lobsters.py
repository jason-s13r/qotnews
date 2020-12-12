import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

if __name__ == '__main__':
    import sys
    sys.path.insert(0,'.')

import requests
from datetime import datetime

from utils import clean

API_HOTTEST = lambda x: 'https://lobste.rs/hottest.json'
API_ITEM = lambda x : 'https://lobste.rs/s/{}.json'.format(x)

SITE_LINK = lambda x : 'https://lobste.rs/s/{}'.format(x)
SITE_AUTHOR_LINK = lambda x : 'https://lobste.rs/u/{}'.format(x)

def api(route, ref=None):
    try:
        r = requests.get(route(ref), timeout=5)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting lobsters API: {}, trying again'.format(str(e)))

    try:
        r = requests.get(route(ref), timeout=15)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting lobsters API: {}'.format(str(e)))
        return False

def feed():
    return [x['short_id'] for x in api(API_HOTTEST) or []]

def unix(date_str):
    return int(datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z').timestamp())

def make_comment(i):
    c = {}
    try:
        c['author'] = i['commenting_user']['username']
    except KeyError:
        c['author'] = ''
    c['score'] = i.get('score', 0)
    try:
        c['date'] = unix(i['created_at'])
    except KeyError:
        c['date'] = 0
    c['text'] = clean(i.get('comment', '') or '')
    c['comments'] = []
    return c

def iter_comments(flat_comments):
    nested_comments = []
    parent_stack = []
    for comment in flat_comments:
        c = make_comment(comment)
        indent = comment['indent_level']

        if indent == 1:
            nested_comments.append(c)
            parent_stack = [c]
        else:
            parent_stack = parent_stack[:indent-1]
            p = parent_stack[-1]
            p['comments'].append(c)
            parent_stack.append(c)
    return nested_comments

def story(ref):
    r = api(API_ITEM, ref)
    if not r: return False

    s = {}
    try:
        s['author'] = r['submitter_user']['username']
        s['author_link'] = SITE_AUTHOR_LINK(s['author'])
    except KeyError:
        s['author'] = ''
        s['author_link'] = ''
    s['score'] = r.get('score', 0)
    try:
        s['date'] = unix(r['created_at'])
    except KeyError:
        s['date'] = 0
    s['title'] = r.get('title', '')
    s['link'] = SITE_LINK(ref)
    s['url'] = r.get('url', '')
    s['comments'] = iter_comments(r['comments'])
    s['num_comments'] = r['comment_count']

    if 'description' in r and r['description']:
        s['text'] = clean(r['description'] or '')

    return s

# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    #print(feed())
    import json
    print(json.dumps(story('fzvd1v')))
    #print(story(20802050))
