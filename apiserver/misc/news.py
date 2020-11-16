import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests
from bs4 import BeautifulSoup
from scrapers import declutter
import extruct

import settings
from utils import clean
from misc.metadata import parse_extruct
from misc.time import unix
from misc.api import xml

def comment(i):
    if 'author' not in i:
        return False

    c = {}
    c['author'] = i.get('author', '')
    c['score'] = i.get('points', 0)
    c['date'] = unix(i.get('date', 0))
    c['text'] = clean(i.get('text', '') or '')
    c['comments'] = [comment(j) for j in i['children']]
    c['comments'] = list(filter(bool, c['comments']))
    return c

def comment_count(i):
    alive = 1 if i['author'] else 0
    return sum([comment_count(c) for c in i['comments']]) + alive

class Base:
    def __init__(url, tz=None):
        self.url = url
        self.tz = tz

    def feed(self, excludes=None):
        return []

    def story(self, ref):
        markup = xml(lambda x: ref)
        if not markup:
            return False

        s = {}
        s['author_link'] = ''
        s['score'] = 0
        s['comments'] = []
        s['num_comments'] = 0
        s['link'] = ref
        s['url'] = ref
        s['date'] = 0

        soup = BeautifulSoup(markup, features='html.parser')
        icon32 = soup.find_all('link', rel="icon", href=True, sizes="32x32")
        icon16 = soup.find_all('link', rel="icon", href=True, sizes="16x16")
        favicon = soup.find_all('link', rel="shortcut icon", href=True)
        others = soup.find_all('link', rel="icon", href=True)
        icons = icon32 + icon16 + favicon + others
        base_url = '/'.join(ref.split('/')[:3])
        icons = list(set([i.get('href') for i in icons]))
        icons = [i if i.startswith('http') else base_url + i for i in icons]

        if icons:
            s['icon'] = icons[0]

        data = extruct.extract(markup)
        s = parse_extruct(s, data)
        if s['date']:
            s['date'] = unix(s['date'], tz=self.tz)

        if 'disqus' in markup:
            try:
                s['comments'] = declutter.get_comments(ref)
                c['comments'] = list(filter(bool, c['comments']))
                s['num_comments'] = comment_count(s['comments'])
            except KeyboardInterrupt:
                raise
            except:
                pass

        if not s['date']:
            return False
        return s
