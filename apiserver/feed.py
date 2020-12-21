import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests
import time
from bs4 import BeautifulSoup
import itertools

import settings
from feeds import hackernews, reddit, tildes, substack, lobsters
from feeds.manual import manual
from feeds.sitemap import Sitemap
from feeds.category import Category
from scrapers import outline
from scrapers.declutter import declutter, headless, simple
from utils import clean
import database

INVALID_DOMAINS = ['youtube.com', 'bloomberg.com', 'wsj.com', 'sec.gov']

substacks = {}
for key, value in settings.SUBSTACK.items():
    substacks[key] = substack.Publication(value['url'])
categories = {}
for key, value in settings.CATEGORY.items():
    categories[key] = Category(value)
sitemaps = {}
for key, value in settings.SITEMAP.items():
    sitemaps[key] = Sitemap(value)

def get_list():
    feeds = {}

    feeds['manual'] = [(x, 'manual', x) for x in manual.feed()]

    if settings.NUM_HACKERNEWS:
        feeds['hackernews'] = [(x, 'hackernews', None) for x in hackernews.feed()[:settings.NUM_HACKERNEWS]]

    if settings.NUM_LOBSTERS:
        feeds['lobsters'] = [(x, 'lobsters', None) for x in lobsters.feed()[:settings.NUM_LOBSTERS]]

    if settings.NUM_REDDIT:
        feeds['reddit'] = [(x, 'reddit', None) for x in reddit.feed()[:settings.NUM_REDDIT]]

    if settings.NUM_TILDES:
        feeds['tildes'] = [(x, 'tildes', x) for x in tildes.feed()[:settings.NUM_TILDES]]

    if settings.NUM_SUBSTACK:
        feeds['substack'] = [(x, 'substack', x) for x in substack.top.feed()[:settings.NUM_SUBSTACK]]

    for key, publication in substacks.items():
        count = settings.SUBSTACK[key]['count']
        feeds[key] = [(x, key, x) for x in publication.feed()[:count]]

    for key, sites in categories.items():
        count = settings.CATEGORY[key].get('count') or 0
        excludes = settings.CATEGORY[key].get('excludes')
        tz = settings.CATEGORY[key].get('tz')
        feeds[key] = [(x, key, u) for x, u in sites.feed(excludes)[:count]]

    for key, sites in sitemaps.items():
        count = settings.SITEMAP[key].get('count') or 0
        excludes = settings.SITEMAP[key].get('excludes')
        feeds[key] = [(x, key, u) for x, u in sites.feed(excludes)[:count]]

    values = feeds.values()
    feed = itertools.chain.from_iterable(itertools.zip_longest(*values, fillvalue=None))
    feed = list(filter(None, feed))
    return feed

def get_article(url):
    scrapers = {
        'headless': headless,
        'simple': simple,
        'outline': outline,
        'declutter': declutter,
    }
    available = settings.SCRAPERS or ['headless', 'simple']
    if 'simple' not in available:
        available += ['simple']

    for scraper in available:
        if scraper not in scrapers.keys():
            continue
        try:
            details = scrapers[scraper].get_details(url)
            if details and details.get('content'):
                return details, scraper
        except KeyboardInterrupt:
            raise
        except:
            pass
    return None, None

def get_content_type(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'X-Forwarded-For': '66.249.66.1',
        }
        return requests.get(url, headers=headers, timeout=5).headers['content-type']
    except:
        pass

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'}
        return requests.get(url, headers=headers, timeout=10).headers['content-type']
    except:
        return ''

def update_source(item, is_manual=False):
    source = {}

    if item.source == 'hackernews':
        return hackernews.story(item.ref)
    elif item.source == 'lobsters':
        return lobsters.story(item.ref)
    elif item.source == 'reddit':
        return reddit.story(item.ref)
    elif item.source == 'tildes':
        return tildes.story(item.ref)
    elif item.source == 'substack':
        return substack.top.story(item.ref)
    elif item.source in categories.keys():
        return categories[item.source].story(item.ref, item.url)
    elif item.source in sitemaps.keys():
        return sitemaps[item.source].story(item.ref, item.url)
    elif item.source in substacks.keys():
        return substacks[item.source].story(item.ref)
    elif item.source == 'manual':
        return manual.story(item.ref)

    return None, None

def scrape_url(url):
    if not get_content_type(url).startswith('text/'):
        logging.info('URL invalid file type / content type:')
        logging.info(url)
        details = { content: f'<a href="{url}">{url}</a>' }
        return details, 'none'

    if any([domain in url for domain in INVALID_DOMAINS]):
        logging.info('URL invalid domain:')
        logging.info(url)
        details = { content: f'<a href="{url}">{url}</a>' }
        return details, 'none'

    logging.info('Getting article ' + url)
    details, scraper = get_article(url)
    if not details:
        return False, False
    details['title'] = clean(details.get('title', ''))
    return details, scraper

if __name__ == '__main__':
    a = get_article('https://blog.joinmastodon.org/2019/10/mastodon-3.0/')
    print(a)

    print('done')
