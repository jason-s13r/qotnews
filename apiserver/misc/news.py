import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import re
import requests
from bs4 import BeautifulSoup
from scrapers.declutter import headless
import extruct

import settings
from utils import clean
from misc.metadata import parse_extruct, get_icons
from misc.time import unix
from misc.api import xml
import misc.stuff as stuff

def clean_comment(comment):
    comment['text'] = clean(comment['text'])
    comment['comments'] = [clean_comments(c) for c in comment['comments']]
    return comment

def comment_count(i):
    alive = 1 if i['author'] else 0
    return sum([comment_count(c) for c in i['comments']]) + alive

class Base:
    def __init__(self, config=dict()):
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
        s['author'] = ''
        s['author_link'] = ''
        s['score'] = 0
        s['comments'] = []
        s['num_comments'] = 0
        s['link'] = urlref
        s['url'] = urlref
        s['date'] = 0
        s['title'] = ''

        icons = get_icons(markup, url=urlref)
        if icons:
            s['icon'] = icons[0]

        data = extruct.extract(markup)
        s = parse_extruct(s, data)
        if s['title']:
            s['title'] = clean(s['title'])
        if s['date']:
            s['date'] = unix(s['date'], tz=self.tz)

        if 'disqus' in markup:
            try:
                s['comments'] = headless.get_comments(urlref)
                s['comments'] = [clean_comments(c) for c in s['comments']]
                s['comments'] = list(filter(bool, s['comments']))
                s['num_comments'] = comment_count(s) - 1
            except KeyboardInterrupt:
                raise
            except:
                pass

        if urlref.startswith('https://www.stuff.co.nz'):
            s['comments'] = stuff.get_json_comments(urlref, markup)
            s['comments'] = list(filter(bool, s['comments']))
            s['num_comments'] = comment_count(s) - 1

        if not s['date']:
            return False
        return s
