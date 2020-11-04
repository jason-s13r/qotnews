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

SUBSTACK_REFERER = 'https://substack.com'
SUBSTACK_API_TOP_POSTS = lambda x: "https://substack.com/api/v1/reader/top-posts"

def author_link(author_id, base_url):
    return f"{base_url}/people/{author_id}"
def api_comments(post_id, base_url):
    return f"{base_url}/api/v1/post/{post_id}/comments?all_comments=true&sort=best_first"
def api_stories(x, base_url): 
    return f"{base_url}/api/v1/archive?sort=new&search=&offset=0&limit=100"

def unix(date_str):
    return int(datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())

def api(route, ref=None, referer=None):
    try:
        headers = {'Referer': referer}
        r = requests.get(route(ref), headers=headers, timeout=5)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting Substack API: {}, trying again'.format(str(e)))

    try:
        r = requests.get(route(ref), headers=headers, timeout=15)
        if r.status_code != 200:
            raise Exception('Bad response code ' + str(r.status_code))
        return r.json()
    except KeyboardInterrupt:
        raise
    except BaseException as e:
        logging.error('Problem hitting Substack API: {}'.format(str(e)))
        return False

def comment(i):
    if 'body' not in i:
        return False

    c = {}
    c['date'] = unix(i.get('date'))
    c['author'] = i.get('name', '')
    c['score'] = i.get('reactions').get('❤')
    c['text'] = clean(i.get('body', '') or '')
    c['comments'] = [comment(j) for j in i['children']]
    c['comments'] = list(filter(bool, c['comments']))

    return c

class Publication:
    def __init__(self, domain):
        self.BASE_DOMAIN = domain

    def feed(self):
        stories = api(lambda x: api_stories(x, self.BASE_DOMAIN), referer=self.BASE_DOMAIN)
        stories = list(filter(None, [i if i.get("audience") == "everyone" else None for i in stories]))
        return [str(i.get("id")) for i in stories or []]

    def story(self, ref):
        stories = api(lambda x: api_stories(x, self.BASE_DOMAIN), referer=self.BASE_DOMAIN)
        stories = list(filter(None, [i if i.get("audience") == "everyone" else None for i in stories]))
        stories = list(filter(None, [i if str(i.get('id')) == ref else None for i in stories]))

        if len(stories) == 0:
            return False

        r = stories[0]
        if not r:
            return False

        s = {}
        s['author'] = ''
        s['author_link'] = ''

        s['date'] = unix(r.get('post_date'))
        s['score'] = r.get('reactions').get('❤')
        s['title'] = r.get('title', '')
        s['link'] = r.get('canonical_url', '')
        s['url'] = r.get('canonical_url', '')
        comments = api(lambda x: api_comments(x, self.BASE_DOMAIN), r.get('id'), referer=self.BASE_DOMAIN)
        s['comments'] = [comment(i) for i in comments.get('comments')]
        s['comments'] = list(filter(bool, s['comments']))
        s['num_comments'] = r.get('comment_count', 0)

        authors = list(filter(None, [self._bylines(byline) for byline in r.get('publishedBylines')]))
        if len(authors):
            s['author'] = authors[0].get('name')
            s['author_link'] = authors[0].get('link')

        return s

    def _bylines(self, b):
        if 'id' not in b:
            return None
        a = {}
        a['name'] = b.get('name')
        a['link'] = author_link(b.get('id'), self.BASE_DOMAIN)
        return a


class Top:
    def feed(self):
        stories = api(SUBSTACK_API_TOP_POSTS, referer=SUBSTACK_REFERER)
        stories = list(filter(None, [i if i.get("audience") == "everyone" else None for i in stories]))
        return [str(i.get("id")) for i in stories or []]

    def story(self, ref):
        stories = api(SUBSTACK_API_TOP_POSTS, referer=SUBSTACK_REFERER)
        stories = list(filter(None, [i if i.get("audience") == "everyone" else None for i in stories]))
        stories = list(filter(None, [i if str(i.get('id')) == ref else None for i in stories]))

        if len(stories) == 0:
            return False

        r = stories[0]
        if not r:
            return False

        s = {}
        pub = r.get('pub')
        base_url = pub.get('base_url')
        s['author'] = pub.get('author_name')
        s['author_link'] = author_link(pub.get('author_id'), base_url)

        s['date'] = unix(r.get('post_date'))
        s['score'] = r.get('score')
        s['title'] = r.get('title', '')
        s['link'] = r.get('canonical_url', '')
        s['url'] = r.get('canonical_url', '')
        comments = api(lambda x: api_comments(x, base_url), r.get('id'), referer=SUBSTACK_REFERER)
        s['comments'] = [comment(i) for i in comments.get('comments')]
        s['comments'] = list(filter(bool, s['comments']))
        s['num_comments'] = r.get('comment_count', 0)

        return s

top = Top()        

# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    top_posts = top.feed()
    print(top.story(top_posts[0]))

    webworm = Publication("https://www.webworm.co/")
    posts = webworm.feed()
    print(posts[:1])
    print(webworm.story(posts[0]))
