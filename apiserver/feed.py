import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

import requests
import time
from bs4 import BeautifulSoup

import settings
from feeds import hackernews, reddit, tildes, substack, manual, news
from scrapers import outline, declutter, local

INVALID_DOMAINS = ['youtube.com', 'bloomberg.com', 'wsj.com']
TWO_DAYS = 60*60*24*2

substacks = {}
for key, value in settings.SUBSTACK.items():
    substacks[key] = substack.Publication(value['url'])
categories = {}
for key, value in settings.CATEGORY.items():
    categories[key] = news.Category(value['url'])
sitemaps = {}
for key, value in settings.SITEMAP.items():
    sitemaps[key] = news.Sitemap(value['url'])

def list():
    feed = []
    if settings.NUM_HACKERNEWS:
        feed += [(x, 'hackernews') for x in hackernews.feed()[:settings.NUM_HACKERNEWS]]

    if settings.NUM_REDDIT:
        feed += [(x, 'reddit') for x in reddit.feed()[:settings.NUM_REDDIT]]

    if settings.NUM_TILDES:
        feed += [(x, 'tildes') for x in tildes.feed()[:settings.NUM_TILDES]]

    if settings.NUM_SUBSTACK:
        feed += [(x, 'substack') for x in substack.top.feed()[:settings.NUM_SUBSTACK]]

    for key, publication in substacks.items():
        count = settings.SUBSTACK[key]['count']
        feed += [(x, key) for x in publication.feed()[:count]]

    for key, sites in categories.items():
        count = settings.CATEGORY[key]['count']
        feed += [(x, key) for x in sites.feed()[:count]]

    for key, sites in sitemaps.items():
        count = settings.SITEMAP[key]['count']
        feed += [(x, key) for x in sites.feed()[:count]]


    return feed

def get_article(url):
    scrapers = {
        'declutter': declutter,
        'outline': outline,
        'local': local,
    }
    available = settings.SCRAPERS or ['local']
    if 'local' not in available:
        available += ['local']

    for scraper in available:
        if scraper not in scrapers.keys():
            continue
        try:
            html = scrapers[scraper].get_html(url)
            if html:
                return html
        except KeyboardInterrupt:
            raise
        except:
            pass
    return ''

def get_content_type(url):
    try:
        headers = {'User-Agent': 'Twitterbot/1.0'}
        return requests.get(url, headers=headers, timeout=2).headers['content-type']
    except:
        pass

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'}
        return requests.get(url, headers=headers, timeout=10).headers['content-type']
    except:
        return ''

def update_story(story, is_manual=False):
    res = {}

    if story['source'] == 'hackernews':
        res = hackernews.story(story['ref'])
    elif story['source'] == 'reddit':
        res = reddit.story(story['ref'])
    elif story['source'] == 'tildes':
        res = tildes.story(story['ref'])
    elif story['source'] == 'substack':
        res = substack.top.story(story['ref'])
    elif story['source'] in categories.keys():
        res = categories[story['source']].story(story['ref'])
    elif story['source'] in sitemaps.keys():
        res = sitemaps[story['source']].story(story['ref'])
    elif story['source'] in substacks.keys():
        res = substacks[story['source']].story(story['ref'])
    elif story['source'] == 'manual':
        res = manual.story(story['ref'])

    if res:
        story.update(res) # join dicts
    else:
        logging.info('Story not ready yet')
        return False

    if story['date'] and not is_manual and story['date'] + TWO_DAYS < time.time():
        logging.info('Story too old, removing')
        return False

    if story.get('url', '') and not story.get('text', ''):
        if not get_content_type(story['url']).startswith('text/'):
            logging.info('URL invalid file type / content type:')
            logging.info(story['url'])
            return False

        if any([domain in story['url'] for domain in INVALID_DOMAINS]):
            logging.info('URL invalid domain:')
            logging.info(story['url'])
            return False

        logging.info('Getting article ' + story['url'])
        story['text'] = get_article(story['url'])
        if not story['text']: return False

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
