import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests

API_TOPSTORIES = lambda x: 'https://hacker-news.firebaseio.com/v0/topstories.json'
API_ITEM = lambda x : 'https://hn.algolia.com/api/v1/items/{}'.format(x)

SITE_LINK = lambda x : 'https://news.ycombinator.com/item?id={}'.format(x)
SITE_AUTHOR_LINK = lambda x : 'https://news.ycombinator.com/user?id={}'.format(x)

def api(route, ref=None):
    try:
        r = requests.get(route(ref), timeout=5)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting hackernews API: {}'.format(str(e)))
        return False

def feed():
    return api(API_TOPSTORIES) or []

def comment(i):
    if 'author' not in i:
        return False

    c = {}
    c['author'] = i.get('author', '')
    c['score'] = i.get('points', 0)
    c['date'] = i.get('created_at_i', 0)
    c['text'] = i.get('text', '')
    c['comments'] = [comment(j) for j in i['children']]
    c['comments'] = list(filter(bool, c['comments']))
    return c

def comment_count(i):
    alive = 1 if i['author'] else 0
    return sum([comment_count(c) for c in i['comments']]) + alive

def story(ref):
    r = api(API_ITEM, ref)
    if not r: return False

    if 'deleted' in r:
        return False
    elif r.get('type', '') != 'story':
        return False

    s = {}
    s['author'] = r.get('author', '')
    s['author_link'] = SITE_AUTHOR_LINK(r.get('author', ''))
    s['score'] = r.get('points', 0)
    s['date'] = r.get('created_at_i', 0)
    s['title'] = r.get('title', '')
    s['link'] = SITE_LINK(ref)
    s['url'] = r.get('url', '')
    s['comments'] = [comment(i) for i in r['children']]
    s['comments'] = list(filter(bool, s['comments']))
    s['num_comments'] = comment_count(s) - 1

    if 'text' in r and r['text']:
        s['text'] = r['text']

    return s

# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    #print(feed())
    #print(story(20763961))
    print(story(20802050))
