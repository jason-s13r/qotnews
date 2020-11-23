import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

if __name__ == '__main__':
    import sys
    sys.path.insert(0,'.')

import requests
from datetime import datetime

from misc.time import unix
from misc.metadata import get_icons
from misc.api import xml, json
from utils import clean

SUBSTACK_REFERER = 'https://substack.com'
SUBSTACK_API_TOP_POSTS = lambda x: "https://substack.com/api/v1/reader/top-posts"

def author_link(author_id, base_url):
    return f"{base_url}/people/{author_id}"
def api_comments(post_id, base_url):
    return f"{base_url}/api/v1/post/{post_id}/comments?all_comments=true&sort=best_first"
def api_stories(x, base_url): 
    return f"{base_url}/api/v1/archive?sort=new&search=&offset=0&limit=100"

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

    def ref_prefix(self, ref):
        return f"{self.BASE_DOMAIN}/#id:{ref}"

    def strip_ref_prefix(self, ref):
        return ref.replace(f"{self.BASE_DOMAIN}/#id:", '')

    def feed(self):
        stories = json(lambda x: api_stories(x, self.BASE_DOMAIN), headers={'Referer': self.BASE_DOMAIN})
        if not stories: return []
        stories = list(filter(None, [i if i.get("audience") == "everyone" else None for i in stories]))
        return [self.ref_prefix(str(i.get("id"))) for i in stories or []]

    def story(self, ref):
        ref = self.strip_ref_prefix(ref)
        stories = json(lambda x: api_stories(x, self.BASE_DOMAIN), headers={'Referer': self.BASE_DOMAIN})
        if not stories: return False
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
        comments = json(lambda x: api_comments(x, self.BASE_DOMAIN), r.get('id'), headers={'Referer': self.BASE_DOMAIN})
        s['comments'] = [comment(i) for i in comments.get('comments')]
        s['comments'] = list(filter(bool, s['comments']))
        s['num_comments'] = r.get('comment_count', 0)

        authors = list(filter(None, [self._bylines(byline) for byline in r.get('publishedBylines')]))
        if len(authors):
            s['author'] = authors[0].get('name')
            s['author_link'] = authors[0].get('link')

        markup = xml(lambda x: s['link'])
        if markup:
            icons = get_icons(markup, url=s['link'])
            if icons:
                s['icon'] = icons[0]

        return s

    def _bylines(self, b):
        if 'id' not in b:
            return None
        a = {}
        a['name'] = b.get('name')
        a['link'] = author_link(b.get('id'), self.BASE_DOMAIN)
        return a


class Top:
    def ref_prefix(self, base_url, ref):
        return f"{base_url}/#id:{ref}"

    def strip_ref_prefix(self, ref):
        if '/#id:' in ref:
            base_url, item = ref.split(f"/#id:")
            return item
        return ref

    def feed(self):
        stories = json(SUBSTACK_API_TOP_POSTS, headers={'Referer': SUBSTACK_REFERER})
        if not stories: return []
        stories = list(filter(None, [i if i.get("audience") == "everyone" else None for i in stories]))
        stories = [dict(id=i.get('id'), base_url=i.get("pub", { 'base_url': '' }).get("base_url")) for i in stories or []]
        return [self.ref_prefix(str(i.get("base_url")), str(i.get("id"))) for i in stories]

    def story(self, ref):
        ref = self.strip_ref_prefix(ref)
        stories = json(SUBSTACK_API_TOP_POSTS, headers={'Referer': SUBSTACK_REFERER})
        if not stories: return False
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
        comments = json(lambda x: api_comments(x, base_url), r.get('id'), headers={'Referer': SUBSTACK_REFERER})
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
    print(webworm.story(posts[0]))
