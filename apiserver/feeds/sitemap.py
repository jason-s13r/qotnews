import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

if __name__ == '__main__':
    import sys
    sys.path.insert(0,'.')

from datetime import datetime
from bs4 import BeautifulSoup

import settings
from utils import clean
from misc.time import unix
from misc.api import xml
from _news import Base

def _get_sitemap_date(a):
    if a.find('lastmod'):
        return a.find('lastmod').text
    if a.find('news:publication_date'):
        return a.find('news:publication_date').text
    if a.find('ns2:publication_date'):
        return a.find('ns2:publication_date').text
    return ''

def _filter_links(links, excludes=None):
    too_old = datetime.now().timestamp() - settings.MAX_STORY_AGE
    links = list(filter(None, [a if _get_sitemap_date(a) else None for a in links]))
    links = list(filter(None, [a if unix(_get_sitemap_date(a)) > too_old else None for a in links]))
    links.sort(key=lambda a: unix(_get_sitemap_date(a)), reverse=True)

    links = [x.find('loc').text for x in links] or []
    links = list(set(links))
    if excludes:
        links = list(filter(None, [None if any(e in link for e in excludes) else link for link in links]))
    return links

def _get_sitemap(feed_url, excludes=None):
    markup = xml(lambda x: feed_url)
    if not markup: return []
    soup = BeautifulSoup(markup, features='lxml')
    links = []
    feed_urls = []
    if soup.find('sitemapindex'):
        sitemap = soup.find('sitemapindex').findAll('sitemap')
        feed_urls = list(filter(None, [a if a.find('loc') else None for a in sitemap]))
    if soup.find('urlset'):
        sitemap = soup.find('urlset').findAll('url')
        links = list(filter(None, [a if a.find('loc') else None for a in sitemap]))

    feed_urls = _filter_links(feed_urls, excludes)
    links = _filter_links(links, excludes)

    for url in feed_urls:
        links += _get_sitemap(url, excludes)
    return list(set(links))

class Sitemap(Base):
    def __init__(self, url, tz=None):
        self.tz = tz
        self.sitemap_url = url

    def feed(self, excludes=None):
        links = []
        if isinstance(self.sitemap_url, str):
            links += _get_sitemap(self.sitemap_url, excludes)
        elif isinstance(self.sitemap_url, list):
            for url in self.sitemap_url:
                links += _get_sitemap(url, excludes)
        return list(set(links))

# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    print("Sitemap: The Spinoff")
    site = Sitemap("https://thespinoff.co.nz/sitemap.xml")
    excludes = [
        'thespinoff.co.nz/sitemap-misc.xml',
        'thespinoff.co.nz/sitemap-authors.xml',
        'thespinoff.co.nz/sitemap-tax-category.xml',
    ]
    posts = site.feed(excludes)
    print(posts[:5])
    print(site.story(posts[0]))

    print("Sitemap: Newshub")
    site = Sitemap([
        'https://www.newshub.co.nz/home/politics.gnewssitemap.xml',
        'https://www.newshub.co.nz/home/new-zealand.gnewssitemap.xml',
        'https://www.newshub.co.nz/home/world.gnewssitemap.xml',
        'https://www.newshub.co.nz/home/money.gnewssitemap.xml',
    ])
    posts = site.feed()
    print(posts[:5])
    print(site.story(posts[0]))
    print(site.story(posts[:-1]))
