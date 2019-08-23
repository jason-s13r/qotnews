import requests

API_TOPSTORIES = lambda x: 'https://hacker-news.firebaseio.com/v0/topstories.json'
API_ITEM = lambda x : 'https://hn.algolia.com/api/v1/items/{}'.format(x)

SITE_LINK = lambda x : 'https://news.ycombinator.com/item?id={}'.format(x)
SITE_AUTHOR_LINK = lambda x : 'https://news.ycombinator.com/user?id={}'.format(x)

def api(route, ref=None):
    r = requests.get(route(ref), timeout=5)
    return r.json()

def feed():
    return api(API_TOPSTORIES)[:30]

def comment(i):
    c = {}
    c['author'] = i.get('author', '')
    c['score'] = i.get('points', 0)
    c['date'] = i.get('created_at_i', 0)
    c['text'] = i.get('text', '')
    c['link'] = SITE_LINK(i['id'])
    c['comments'] = [comment(j) for j in i['children']]
    return c

def comment_count(i):
    alive = 1 if i['author'] else 0
    return sum([comment_count(c) for c in i['comments']]) + alive

def story(ref):
    r = api(API_ITEM, ref)

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
    s['source'] = 'hackernews'
    s['url'] = r.get('url', '')
    s['comments'] = [comment(i) for i in r['children']]
    s['num_comments'] = comment_count(s) - 1

    if 'text' in r and r['text']:
        s['text'] = r['text']

    return s

if __name__ == '__main__':
    print(story(20763961))
