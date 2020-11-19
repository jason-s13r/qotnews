import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import re
import requests
from bs4 import BeautifulSoup
from scrapers import declutter
import extruct

import settings
from utils import clean
from misc.metadata import parse_extruct
from misc.time import unix
from misc.api import xml
import misc.stuff as stuff

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
    def __init__(config):
        self.config = config
        self.url = config.get('url')
        self.tz = config.get('tz')

    def get_id(self, link):
        patterns = self.config.get('patterns')
        if not patterns:
            return link
        patterns = [re.compile(p) for p in patterns]
        patterns = list(filter(None, [p.match(link) for p in patterns]))
        patterns = list(set([':'.join(p.groups()) for p in patterns]))
        if not patterns:
            return link
        return patterns[0]

    def feed(self, excludes=None):
        return []

    def story(self, ref, urlref):
        if urlref is None:
            return False
        markup = xml(lambda x: urlref)
        if not markup:
            return False

        s = {}
        s['author_link'] = ''
        s['score'] = 0
        s['comments'] = []
        s['num_comments'] = 0
        s['link'] = urlref
        s['url'] = urlref
        s['date'] = 0

        soup = BeautifulSoup(markup, features='html.parser')
        icon32 = soup.find_all('link', rel="icon", href=True, sizes="32x32")
        icon16 = soup.find_all('link', rel="icon", href=True, sizes="16x16")
        favicon = soup.find_all('link', rel="shortcut icon", href=True)
        others = soup.find_all('link', rel="icon", href=True)
        icons = icon32 + icon16 + favicon + others
        base_url = '/'.join(urlref.split('/')[:3])
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
                s['comments'] = declutter.get_comments(urlref)
                s['comments'] = list(filter(bool, s['comments']))
                s['num_comments'] = comment_count(s['comments'])
            except KeyboardInterrupt:
                raise
            except:
                pass

        if urlref.startswith('https://www.stuff.co.nz'):
            s['comments'] = stuff.get_comments(urlref)
            s['comments'] = list(filter(bool, s['comments']))
            s['num_comments'] = len(s['comments'])

        if not s['date']:
            return False
        return s
