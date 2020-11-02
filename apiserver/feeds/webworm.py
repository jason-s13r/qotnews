import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

if __name__ == '__main__':
    import sys
    sys.path.insert(0,'.')

import requests

from utils import clean

WEBWORM_DOMAIN = "https://www.webworm.co"

API_STORIES = lambda x: f'{WEBWORM_DOMAIN}/api/v1/archive?sort=new&search=&offset=0&limit=100'
#API_ITEM = lambda x : f'https://hn.algolia.com/api/v1/items/{x}'
API_ITEM_COMMENTS = lambda x: f"{WEBWORM_DOMAIN}/api/v1/post/{x}/comments?all_comments=true&sort=best_first"

SITE_LINK = lambda x: f'{WEBWORM_DOMAIN}/p/{x}'
SITE_AUTHOR_LINK = lambda x : f'{WEBWORM_DOMAIN}/people/{x}'

def api(route, ref=None):
    try:
        r = requests.get(route(ref), timeout=5)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting Substack API: {}, trying again'.format(str(e)))

    try:
        r = requests.get(route(ref), timeout=15)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting Substack API: {}'.format(str(e)))
        return False

def feed():
    stories = api(API_STORIES)
    stories = list(filter(None, [None if i.get("audience") == "only_paid" else i for i in stories]))
    return [str(i.get("id")) for i in stories or []]

def bylines(b):
    if 'id' not in b:
        return None
    a = {}
    a['name'] = b.get('name')
    a['link'] = SITE_AUTHOR_LINK(b.get('id'))
    return a

def comment(i):
    if 'body' not in i:
        return False

    c = {}
    c['author'] = i.get('name', '')
    c['score'] = o.get('reactions').get('❤')
    c['date'] = i.get('created_at_i', 0)
    c['text'] = clean(i.get('body', '') or '')
    c['comments'] = [comment(j) for j in i['children']]
    c['comments'] = list(filter(bool, c['comments']))
    return c

def comment_count(i):
    alive = 1 if i['author'] else 0
    return sum([comment_count(c) for c in i['comments']]) + alive

def story(ref):
    stories = api(API_STORIES)
    stories = list(filter(None, [None if i.get("audience") == "only_paid" else i for i in stories]))
    stories = list(filter(None, [i if str(i.get('id')) == ref else None for i in stories]))

    if len(stories) == 0:
        print("no items")
        return False

    r = stories[0]
    if not r:
        print("not r")
        return False

    s = {}
    authors = list(filter(None, [bylines(byline) for byline in r.get('publishedBylines')]))
    s['author'] = ''
    s['author_link'] = ''
    if len(authors):
        s['author'] = authors[0].get('name')
        s['author_link'] = authors[0].get('link')
    s['score'] = r.get('reactions').get('❤')
    s['date'] = r.get('post_date', 0)
    s['title'] = r.get('title', '')
    s['link'] = r.get('canonical_url', '')
    s['url'] = r.get('canonical_url', '')
    s['comments'] = [comment(i) for i in api(API_ITEM_COMMENTS, r.get('id'))]
    s['comments'] = list(filter(bool, s['comments']))
    s['num_comments'] = r.get('comment_count', 0)

    if 'text' in r and r['text']:
        s['text'] = clean(r['text'] or '')

    return s

# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    stories = feed()
    print(stories)
    print(story(stories[0]))
