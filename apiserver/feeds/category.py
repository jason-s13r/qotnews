import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)

if __name__ == '__main__':
    import sys
    sys.path.insert(0,'.')

from bs4 import BeautifulSoup

import settings
from utils import clean
from misc.api import xml
from _news import Base

def _filter_links(links, category_url, excludes=None):
    links = list(filter(None, [link if link.startswith(category_url) else None for link in links]))
    links = list(filter(None, [link if link != category_url else None for link in links]))
    links = list(set(links))
    if excludes:
        links = list(filter(None, [None if any(e in link for e in excludes) else link for link in links]))
    return links

def _get_category(category_url, excludes=None):
    base_url = '/'.join(category_url.split('/')[:3])
    markup = xml(lambda x: category_url)
    if not markup: return []
    soup = BeautifulSoup(markup, features='html.parser')
    links = soup.find_all('a', href=True)
    links = [link.get('href') for link in links]
    links = [f"{base_url}{link}" if link.startswith('/') else link for link in links]
    links = _filter_links(links, category_url, excludes)
    return links

class Category(Base):
    def __init__(self, url, tz=None):
        self.tz = tz
        self.category_url = url

    def feed(self, excludes=None):
        links = []
        if isinstance(self.category_url, str):
            links += _get_category(self.category_url, excludes)
        elif isinstance(self.category_url, list):
            for url in self.category_url:
                links += _get_category(url, excludes)
        return list(set(links))


# scratchpad so I can quickly develop the parser
if __name__ == '__main__':
    print("Category: RadioNZ")
    site = Category("https://www.rnz.co.nz/news/")
    excludes = [
        'rnz.co.nz/news/sport',
        'rnz.co.nz/weather',
        'rnz.co.nz/news/weather',
    ]
    posts = site.feed(excludes)
    print(posts[:5])
    print(site.story(posts[0]))

    print("Category: Newsroom")
    site = Category("https://www.newsroom.co.nz/news/", tz='Pacific/Auckland')
    posts = site.feed()
    print(posts[:5])
    print(site.story(posts[0]))


