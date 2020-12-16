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
        feeds['hackernews'] = [(x, 'hackernews', x) for x in hackernews.feed()[:settings.NUM_HACKERNEWS]]

    if settings.NUM_LOBSTERS:
        feed += [(x, 'lobsters', x) for x in lobsters.feed()[:settings.NUM_LOBSTERS]]

    if settings.NUM_REDDIT:
        feeds['reddit'] = [(x, 'reddit', x) for x in reddit.feed()[:settings.NUM_REDDIT]]

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

def update_story(story, is_manual=False, urlref=None):
    res = {}

    if story['source'] == 'hackernews':
        res = hackernews.story(story['ref'])
    elif story['source'] == 'lobsters':
        res = lobsters.story(story['ref'])
    elif story['source'] == 'reddit':
        res = reddit.story(story['ref'])
    elif story['source'] == 'tildes':
        res = tildes.story(story['ref'])
    elif story['source'] == 'substack':
        res = substack.top.story(story['ref'])
    elif story['source'] in categories.keys():
        res = categories[story['source']].story(story['ref'], urlref)
    elif story['source'] in sitemaps.keys():
        res = sitemaps[story['source']].story(story['ref'], urlref)
    elif story['source'] in substacks.keys():
        res = substacks[story['source']].story(story['ref'])
    elif story['source'] == 'manual':
        res = manual.story(story['ref'])

    if res:
        story.update(res) # join dicts
    else:
        logging.info('Story not ready yet')
        return False

    if story['date'] and not is_manual and story['date'] + settings.MAX_STORY_AGE < time.time():
        logging.info('Story too old, removing')
        return False

    has_url = story.get('url') or False
    has_text = story.get('text') or False
    #is_simple = story.get('scaper', '') == 'simple'
    
    if has_url and not has_text:
        if not get_content_type(story['url']).startswith('text/'):
            logging.info('URL invalid file type / content type:')
            logging.info(story['url'])
            return False

        if any([domain in story['url'] for domain in INVALID_DOMAINS]):
            logging.info('URL invalid domain:')
            logging.info(story['url'])
            return False

        logging.info('Getting article ' + story['url'])
        details, scraper = get_article(story['url'])
        if not details: return False
        story['scraper'] = scraper
        story['text'] = details.get('content', '')
        if not story['text']: return False
        story['last_update'] = time.time()
        story['excerpt'] = details.get('excerpt', '')
        story['scraper_link'] = details.get('scraper_link', '')
        meta = details.get('meta')
        if meta:
            og = meta.get('og')
            story['image'] = meta.get('image', '')
            if og: 
                story['image'] = og.get('og:image', meta.get('image', ''))
            links = meta.get('links', [])
            if links:
                story['meta_links'] = links
                manual.add_links(links)

    return True

if __name__ == '__main__':
    #test_news_cache = {}
    #nid = 'jean'
    #ref = 20802050
    #source = 'hackernews'
    #test_news_cache[nid] = dict(id=nid, ref=ref, source=source)
    #news_story = test_news_cache[nid]
    #update_story(news_story)

    #print(get_article('https://www.bloomberg.com/news/articles/2019-09-23/xi-s-communists-under-pressure-as-high-prices-hit-china-workers'))

    a = get_article('https://blog.joinmastodon.org/2019/10/mastodon-3.0/')
    print(a)

    print('done')
